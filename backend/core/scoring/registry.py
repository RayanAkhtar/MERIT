from typing import Dict, Any, List, Optional
import re
from .base import BaseMetric
from .language_expertise import LanguageExpertiseMetric
from .technology_stack import TechnologyStackMetric
from .education_metric import EducationMetric
from .soft_skills_metric import SoftSkillsMetric
from .professional_gravity import ProfessionalGravityMetric
from .intelligence_metrics import (
    ExperienceMetric, ProjectsMetric, TechSkillsMetric,
    GithubComplexityMetric, GithubAlignmentMetric, GithubImpactMetric,
    LinkedinExtracurricularMetric, LinkedinNetworkMetric
)
from .keyword_stuffing import KeywordStuffingDetector

class ScoringRegistry:
    def __init__(self):
        self.metric_templates: Dict[str, BaseMetric] = {}
        # Register core templates
        self.register(LanguageExpertiseMetric())
        self.register(TechnologyStackMetric())
        self.register(EducationMetric())
        # self.register(SoftSkillsMetric())
        self.register(ProfessionalGravityMetric())

        
        # Register Intelligence Metrics
        self.register(ExperienceMetric())
        self.register(ProjectsMetric())
        self.register(TechSkillsMetric())
        self.register(GithubComplexityMetric())
        self.register(GithubAlignmentMetric())
        self.register(GithubImpactMetric())
        self.register(LinkedinExtracurricularMetric())
        self.register(LinkedinNetworkMetric())
        
        self.stuffing_detector = KeywordStuffingDetector()

    def register(self, metric: BaseMetric):
        self.metric_templates[metric.id] = metric

    def _get_metric_for_key(self, key: str, job_requirements: Dict[str, Any]) -> Optional[BaseMetric]:
        """
        Determines which metric template should handle a specific config key.
        """
        # check for a direct match first
        if key in self.metric_templates:
            return self.metric_templates[key]
        
        # requirement keys (e.g. 'req_python', 'req_AWS')
        if key.startswith("req_"):
            # Try to find which category this requirement belongs to in the JD
            clean_name = key.replace("req_", "").replace("_", " ").lower()
            jd_metrics = job_requirements.get("metrics", {})
            
            # TODO: at some point, get rid of experience, responsibilities and requirements since they are unused
            # Helper to extract names from potentially complex JD value lists
            def extract_names(items):
                names = []
                for item in items:
                    if isinstance(item, dict):

                        val = item.get("value") or item.get("name") or ""
                        names.append(str(val).lower())
                    else:
                        names.append(str(item).lower())
                return names

            langs = extract_names(jd_metrics.get("Languages", {}).get("value", []))
            if clean_name in langs:
                return self.metric_templates.get("languages")
            
            techs = extract_names(jd_metrics.get("Technologies", {}).get("value", []))
            if any(clean_name in t or t in clean_name for t in techs):
                return self.metric_templates.get("technologies")
            
            # soft = extract_names(jd_metrics.get("Soft Skills", {}).get("value", []))
            # if any(clean_name in s or s in clean_name for s in soft):
            #     return self.metric_templates.get("soft_skills")

                
            # Default to tech stack if unknown requirement
            return self.metric_templates.get("technologies")

        return None

    def run_all(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], 
                active_metrics: Optional[Dict[str, bool]] = None, weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Runs all active metrics and maps them to the provided weights.
        """
        results = {}
        total_weighted_score = 0.0
        total_weight = 0.0

        # Handle active_metrics as a dict (as provided in user example)
        if isinstance(active_metrics, dict):
            keys_to_run = [k for k, v in active_metrics.items() if v is True]
        else:
            # Fallback for list-based active_metrics
            keys_to_run = active_metrics if active_metrics else list(self.metric_templates.keys())

        if not keys_to_run:
            return {
                "overall_score": 0.0, 
                "metrics": {}, 
                "sources_used": [],
                "calculation_summary": {
                    "weighted_sum": 0,
                    "total_weight": 0,
                    "formula": "N/A",
                    "logic": "No active metrics selected."
                }
            }

        from .constants import SCORING_CONSTANTS
        integrity_cfg = SCORING_CONSTANTS.get("INTEGRITY", {"SQUATTER_PENALTY": 0.2, "SCORE_CAP": 1.0})

        # Pre-calculate integrity audit to pass to individual metrics
        target_keywords = []
        jd_metrics = job_requirements.get("metrics", {})
        for category in ["Languages", "Technologies"]:
            vals = jd_metrics.get(category, {}).get("value", [])
            for v in vals:
                if isinstance(v, dict):
                    target_keywords.append(v.get("value"))
                else:
                    target_keywords.append(v)
        
        candidate_cv = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        stuffing_audit = self.stuffing_detector.analyze(candidate_cv, target_keywords)

        for key in keys_to_run:
            metric = self._get_metric_for_key(key, job_requirements)
            if not metric:
                continue
                
            active_items = None
            if key.startswith("req_"):
                clean_name = key.replace("req_", "").replace("_", " ")
                active_items = [clean_name]

            res = metric.calculate(candidate_data, job_requirements, active_items=active_items, stuffing_audit=stuffing_audit) or {}
            raw_weight = weights.get(key, 0.0) if (weights and weights.get(key) is not None) else 0.0
            
            # CRITICAL FIX: Cap individual metric scores at 1.0 to prevent total > 100%
            metric_score = min(integrity_cfg.get("SCORE_CAP", 1.0), float(res.get("score") or 0.0))
            
            total_weighted_score += metric_score * raw_weight
            total_weight += raw_weight
            
            merged_res = {**res}
            merged_res.update({
                "name": active_items[0] if (active_items and len(active_items) > 0) else (metric.name if metric else "Unknown Metric"),
                "weight": raw_weight,
                "score": metric_score,
                "formula": res.get("calculation_formula", "Simple Weighted Average"),
                "technical_formula": res.get("technical_formula", ""),
                "glossary": res.get("glossary", []),
                "breakdown": res.get("breakdown", []),
                "sources_used": res.get("sources_used", []),
                "improvements": res.get("improvements", [])
            })
            results[key] = merged_res

        # Recalculate baseline overall score
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        # integrity audit
        target_keywords = []
        jd_metrics = job_requirements.get("metrics", {})
        for category in ["Languages", "Technologies"]:
            vals = jd_metrics.get(category, {}).get("value", [])
            for v in vals:
                if isinstance(v, dict):
                    target_keywords.append(v.get("value") or v.get("name") or "")
                else:
                    target_keywords.append(str(v))

        for key in keys_to_run:
            if key.startswith("req_"):
                target_keywords.append(key.replace("req_", "").replace("_", " "))
        
        target_keywords = list(set([k for k in target_keywords if k and str(k).strip()]))
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        stuffing_audit = self.stuffing_detector.analyze(cv_text, target_keywords)

        # Identity Consistency Audit
        import difflib
        cv_name = str(candidate_data.get("name", "")).lower().strip()
        gh_profile = candidate_data.get("github_enriched") or candidate_data.get("github_profile") or {}
        gh_name = str(gh_profile.get("name", "")).lower().strip()
        
        identity_penalty = 0.0
        similarity = 1.0
        
        # Only apply squatter penalty if we actually found a name on the profile
        # to avoid penalising missing data as a mismatch.
        valid_gh_name = gh_name and gh_name != "none" and len(gh_name) > 2
        
        if valid_gh_name and cv_name:
            similarity = difflib.SequenceMatcher(None, cv_name, gh_name).ratio()
            # If similarity < 70% and no substring match, apply the Veto
            if similarity < 0.7 and cv_name not in gh_name and gh_name not in cv_name:
                identity_penalty = integrity_cfg.get("SQUATTER_PENALTY", 0.20)

        # Flag stuffing penalties in the individual metrics for UI transparency
        # The actual score deduction is handled natively by the metric templates 
        # (e.g. LanguageExpertiseMetric) at the signal level.
        for term_audit in stuffing_audit["flagged_terms"]:
            term = term_audit["term"].lower().replace(" ", "_")
            req_key = f"req_{term}"
            p_val = term_audit["penalty_contribution"]
            audit_data = {
                "term": term_audit["term"],
                "count": term_audit["count"],
                "density": term_audit["density"],
                "limit": integrity_cfg.get("OCCURRENCE_LIMIT", 4),
                "penalty_per": integrity_cfg.get("PENALTY_PER_OCCURRENCE", 0.08)
            }

            # Flag the specific requirement (e.g. req_python)
            if req_key in results:
                m = results[req_key]
                m["integrity_penalty_applied"] = True
                m["integrity_penalty_value"] = p_val
                m["integrity_audit_details"] = audit_data

            # Flag the parent category metric if applicable
            jd_metrics = job_requirements.get("metrics", {})
            for cat_id, cat_name in [("languages", "Languages"), ("technologies", "Technologies")]:
                if cat_id in results:
                    cat_vals = [v.get("value") if isinstance(v, dict) else v for v in jd_metrics.get(cat_name, {}).get("value", [])]
                    if any(str(v).lower() == term_audit["term"].lower() for v in cat_vals):
                        results[cat_id]["integrity_penalty_applied"] = True
                        # If multiple terms are stuffed, we show the highest penalty audit
                        if p_val > results[cat_id].get("integrity_penalty_value", 0):
                            results[cat_id]["integrity_penalty_value"] = p_val
                            results[cat_id]["integrity_audit_details"] = audit_data

        # Recalculate finalized overall score after stuffing penalties
        weighted_sum = sum((m.get("score") or 0.0) * (m.get("weight") or 0.0) for m in results.values())
        raw_average = weighted_sum / total_weight if total_weight > 0 else 0.0
        
        # apply global identity veto (deduct from the average)
        final_adjusted_score = max(0.0, raw_average - identity_penalty)

        stuffing_notes = ""
        if identity_penalty > 0:
            stuffing_notes = f"SQUATTER PENALTY: dock of {int(identity_penalty*100)}% applied. "
        if stuffing_audit["is_stuffed"]:
            stuffing_notes += "INTEGRITY PENALTY: Keyword stuffing detected."

        # final logic string showing the actual deduction
        logic_formula = f"({weighted_sum:.2f} pts / {total_weight:.1f} max)"
        if identity_penalty > 0:
            logic_formula = f"[{logic_formula} - {identity_penalty:.2f} Veto]"
            
        return {
            "overall_score": round(final_adjusted_score, 3),
            "integrity_penalty": stuffing_audit["penalty"] + identity_penalty, 
            "calculation_summary": {
                "formula": "SUM(PenalisedMetricScore * Weight) / SUM(Weights) - IdentityPenalty",
                "weighted_sum": weighted_sum,
                "total_weight": total_weight,
                "base_score": overall_score,
                "raw_average": raw_average,
                "integrity_penalty": stuffing_audit["penalty"] + identity_penalty,
                "identity_penalty": identity_penalty,
                "identity_audit_details": {
                    "cv_name": cv_name.title(),
                    "profile_name": gh_name.title(),
                    "similarity": round(similarity * 100, 1),
                    "status": "MISMATCH" if identity_penalty > 0 else "VERIFIED"
                } if gh_name else None,
                "stuffing_audit": stuffing_audit["flagged_terms"],
                "logic": f"Final Match % [CONSISTENCY_SYNC_ACTIVE] = {logic_formula} = {final_adjusted_score:.3f}. {stuffing_notes}"
            },
            "metrics": results
        }

# Global instance
scoring_registry = ScoringRegistry()
