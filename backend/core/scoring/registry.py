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

        for key in keys_to_run:
            metric = self._get_metric_for_key(key, job_requirements)
            if not metric:
                # If no handler, skip or provide a zero score
                continue
                
            # figure out which bits are active for this metric
            active_items = None
            if key.startswith("req_"):
                # pass the specific item to the metric
                clean_name = key.replace("req_", "").replace("_", " ")
                active_items = [clean_name]

            # scoring
            # pass the specific key as context if needed
            res = metric.calculate(candidate_data, job_requirements, active_items=active_items) or {}
            
            # apply the weight from the config
            raw_weight = weights.get(key, 0.0) if (weights and weights.get(key) is not None) else 0.0
            
            metric_score = float(res.get("score") or 0.0)
            total_weighted_score += metric_score * raw_weight
            total_weight += raw_weight
            
            # merge the results into the final dict for the frontend
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

        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        # penalty for keyword stuffing so people can't game the system
        target_keywords = []
        jd_metrics = job_requirements.get("metrics", {})
        for category in ["Languages", "Technologies"]:
            vals = jd_metrics.get(category, {}).get("value", [])
            for v in vals:
                if isinstance(v, dict):
                    target_keywords.append(v.get("value") or v.get("name") or "")
                else:
                    target_keywords.append(str(v))

        
        # check specific requirements from the active keys
        for key in keys_to_run:
            if key.startswith("req_"):
                target_keywords.append(key.replace("req_", "").replace("_", " "))
        
        # Deduplicate and filter out empty strings to prevent the '200% density' bug
        target_keywords = list(set([k for k in target_keywords if k and str(k).strip()]))


        # use the raw cv text for the most accurate count
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        stuffing_audit = self.stuffing_detector.analyze(cv_text, target_keywords)
        # print(f"DEBUG [Registry]: Stuffing Audit -> Penalty: {stuffing_audit['penalty']} | Flagged: {len(stuffing_audit['flagged_terms'])}")
        for t in stuffing_audit['flagged_terms']:
            # print(f"  - Flagged: {t['term']} ({t['count']}x)")
            pass
        
        penalty = stuffing_audit["penalty"]
        final_adjusted_score = max(0.0, overall_score - penalty)
        
        # wrap up the metrics and shove the penalties in so recruiters can see why
        flagged_keys = []
        for term_audit in stuffing_audit["flagged_terms"]:
            term = term_audit["term"].lower().replace(" ", "_")
            req_key = f"req_{term}"
            if req_key in results:
                m = results[req_key]
                p_val = term_audit["penalty_contribution"]
                
                # update score (penalise once)
                old_score = m["score"]
                m["score"] = max(0.0, old_score - p_val)
                
                # update left-hand signals
                m["breakdown"].append({
                    "item": "Authenticity & Integrity Audit",
                    "notes": f"INTEGRITY ENGINE: Detected {term_audit['count']} occurrences of '{term_audit['term']}', which exceeds the natural repetition limit ({self.stuffing_detector.cfg['OCCURRENCE_LIMIT']}). A penalty of 2% per excess occurrence was applied to ensure the match remains authentic and not gamed via keyword stuffing.",
                    "source_details": [
                        {
                            "source": "INTEGRITY AUDIT",
                            "explanation": f"Excessive keyword repetition detected for '{term_audit['term']}'. Frequency: {term_audit['count']}x | Density: {term_audit['density']}.",
                            "score": -p_val
                        }
                    ]
                })
                
                # add metadata for frontend highlighting
                m["integrity_penalty_applied"] = True
                m["integrity_penalty_value"] = p_val
                m["integrity_audit_details"] = {
                    "count": term_audit['count'],
                    "limit": self.stuffing_detector.cfg['OCCURRENCE_LIMIT'],
                    "penalty_per": self.stuffing_detector.cfg['PENALTY_PER_OCCURRENCE'],
                    "term": term_audit['term']
                }
                
                # update right-hand formula
                if m.get("technical_formula"):
                    m["technical_formula"] = f"({m['technical_formula']}) - {p_val:.2f} [Integrity Penalty] = {m['score']:.2f}"
                else:
                    m["technical_formula"] = f"{old_score:.2f} - {p_val:.2f} [Integrity Penalty] = {m['score']:.2f}"
                
                flagged_keys.append(req_key)

        # recalculate overall score based on the finalised (potentially penalised) metrics
        new_total_weighted_score = sum((m.get("score") or 0.0) * (m.get("weight") or 0.0) for m in results.values())
        final_adjusted_score = new_total_weighted_score / total_weight if total_weight > 0 else 0.0

        stuffing_notes = ""
        if stuffing_audit["is_stuffed"]:
            terms = ", ".join([f"{t['term']} ({t['count']}x)" for t in stuffing_audit["flagged_terms"][:3]])
            stuffing_notes = f"INTEGRITY PENALTY APPLIED: Multiple metrics flagged for keyword repetition: {terms}"

        return {
            "overall_score": final_adjusted_score,
            "integrity_penalty": penalty, 
            "calculation_summary": {
                "formula": "SUM(PenalisedMetricScore * Weight) / SUM(Weights)",
                "weighted_sum": new_total_weighted_score,
                "total_weight": total_weight,
                "base_score": overall_score,
                "integrity_penalty": penalty,
                "stuffing_audit": stuffing_audit["flagged_terms"],
                "logic": f"Final Match % [CONSISTENCY_SYNC_ACTIVE] = ({new_total_weighted_score:.2f} pts) / ({total_weight:.1f} max). {stuffing_notes}"
            },
            "metrics": results
        }

# Global instance
scoring_registry = ScoringRegistry()
