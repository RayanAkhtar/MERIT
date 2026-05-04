import math
from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS
from core.fusion.bayesian import Evidence

class TechnologyStackMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "technologies"

    @property
    def name(self) -> str:
        return "Technology & Tool proficiency"

    @property
    def description(self) -> str:
        return "Analyses expertise in specific libraries, frameworks, and tools mentioned in the job description."

    def _calculate_recency_multiplier(self, tech: str, candidate_data: Dict[str, Any]) -> tuple[float, str]:
        import datetime
        current_year = datetime.datetime.now().year
        tech_lower = tech.lower()
        
        # Use language recency config as baseline
        cfg = SCORING_CONSTANTS["LANGUAGES"]["RECENCY"]
        
        # check github activity (scans repo names and descriptions for the tech)
        gh_profile = candidate_data.get("github_profile") or {}
        gh_repos = candidate_data.get("github_projects") or []
        last_gh_year = 0
        for repo in gh_repos:
            r_name = str(repo.get("name") or "").lower()
            r_desc = str(repo.get("description") or "").lower()
            if tech_lower in r_name or tech_lower in r_desc:
                # Approximate year from updated_at or similar
                u_at = repo.get("updated_at")
                if u_at and isinstance(u_at, str) and len(u_at) >= 4:
                    last_gh_year = max(last_gh_year, int(u_at[:4]))
        
        # then check linkedin history
        li_experience = candidate_data.get("linkedin_experience") or []
        last_li_year = 0
        for i, exp in enumerate(li_experience[:3]):
            desc = (exp.get("description") or "").lower()
            pos = (exp.get("position") or "").lower()
            if tech_lower in desc or tech_lower in pos:
                last_li_year = max(last_li_year, current_year - i)
        
        latest_activity = max(last_gh_year, last_li_year)
        if latest_activity == 0: 
            return 1.0, "Historical claim (No recent temporal activity)"
            
        years_since = float(current_year - latest_activity)
        
        # Exponential decay: Score * e^(-lambda * t)
        decay_mult = math.exp(-cfg["DECAY_LAMBDA"] * years_since)
        
        if years_since <= cfg["ACTIVE_THRESHOLD"]:
            return cfg["BOOST_ACTIVE"], f"Active Proficiency (Last seen {latest_activity})"
            
        # Round it to 2 decimal places for the UI
        decay_mult = round(decay_mult, 2)
        
        if years_since <= 3:
            return decay_mult, f"Temporal Decay (Last used ~{int(years_since)} years ago)"
        
        return max(0.2, decay_mult), f"Legacy Skill ({int(years_since)}+ years since last activity)"

    def _count_mentions(self, tech: str, cv_text: str) -> int:
        if not cv_text: return 0
        import re
        tech_lower = tech.lower()

        # count occurrences with word boundaries to avoid substrings
        pattern = rf"\b{re.escape(tech_lower)}\b"
        return len(re.findall(pattern, cv_text.lower()))

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        breakdown = []
        sources_used = ["CV"]
        cfg = SCORING_CONSTANTS["TECH_STACK"]
        
        jd_metrics = job_requirements.get("metrics", {})
        tech_config = jd_metrics.get("Technologies", {}).get("value", [])
        
        target_tech = tech_config
        if active_items:
            active_set = {a.lower() for a in active_items}
            # Handle list of dicts
            target_tech = []
            for t in tech_config:
                t_val = t.get("value") if isinstance(t, dict) else t
                if t_val and str(t_val).lower() in active_set:
                    target_tech.append(t)
            
            for a in active_items:
                if a.lower() not in {str(t.get("value") if isinstance(t, dict) else t).lower() for t in tech_config if t is not None}:
                    target_tech.append(a)


        if not target_tech:
             return {"score": 0.0, "breakdown": [], "sources_used": sources_used}

        raw_skills = candidate_data.get("skills") or []
        cv_skills = [str(s).lower() for s in raw_skills if s is not None]
        li_exp = candidate_data.get("linkedin_experience", [])
        li_text = " ".join([str(e.get("description") or "") for e in li_exp]).lower()
        if li_exp: sources_used.append("LinkedIn")

        total_item_score = 0.0
        for tech in target_tech:
            # handle dict or string
            tech_val = tech.get("value") if isinstance(tech, dict) else tech
            tech_lower = str(tech_val).lower()
            tech_display = tech_val

            
            # cv signal
            cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
            mentions = self._count_mentions(tech_val, cv_text)

            has_cv = mentions > 0
            
            has_li = tech_lower in li_text and len(tech_lower) > 2
            
            item_sources = []
            source_details = [
                {
                    "name": tech_display,
                    "source": f"Tooling Detail: {tech_display}",
                    "score": 1.0 if (has_cv or has_li) else 0.0,
                    "explanation": f"Analysing professional footprint for {tech_display}."
                }

            ]
            
            # --- Bayesian Evidence Aggregation ---
            evidence = []
            conf = SCORING_CONSTANTS["FUSION"]["SOURCE_CONFIDENCE"]["TECHNICAL_SKILLS"]
            
            # CV signal
            if has_cv:
                item_sources.append("CV")
                evidence.append(Evidence(source="CV", confidence=conf["CV"], strength=1.0))
                source_details.append({
                    "source": "CV",
                    "score": 1.0,
                    "trust": conf["CV"],
                    "derivation": f"Binary Presence (Mentions: {mentions} >= 1)",
                    "explanation": f"Found {mentions} occurrences in document.",
                    "weighting": f"Self-reported (Conf: {conf['CV']:.1f})"
                })
            
            # LinkedIn Evidence
            if has_li:
                item_sources.append("LinkedIn")
                evidence.append(Evidence(source="LinkedIn", confidence=conf["LINKEDIN"], strength=1.0))
                start_idx = max(0, li_text.find(tech_lower) - 40)
                end_idx = min(len(li_text), li_text.find(tech_lower) + 60)
                snippet = li_text[start_idx:end_idx].strip()
                source_details.append({
                    "source": "LinkedIn",
                    "score": 1.0,
                    "trust": conf["LINKEDIN"],
                    "derivation": "Binary Presence (Mentions in history = 1.0)",
                    "explanation": f"Found in experience history: \"...{snippet}...\" (Normalised: 1.00)",
                    "weighting": f"Professional Record (Conf: {conf['LINKEDIN']:.1f})"
                })

            # GitHub Evidence
            gh_repos = candidate_data.get("github_projects") or []
            has_gh = any(tech_lower in str(r.get("name") or "").lower() or tech_lower in str(r.get("description") or "").lower() for r in gh_repos)
            if has_gh:
                item_sources.append("GitHub")
                evidence.append(Evidence(source="GitHub", confidence=conf["GITHUB"], strength=1.0))
                source_details.append({
                    "source": "GitHub",
                    "score": 1.0,
                    "trust": conf["GITHUB"],
                    "derivation": "Binary Presence (Relevant project found = 1.0)",
                    "explanation": f"Found dedicated repositories or mentions in projects.",
                    "weighting": f"Work Sample (Conf: {conf['GITHUB']:.1f})"
                })

            # skill decay
            recency_mult, recency_note = self._calculate_recency_multiplier(tech_val, candidate_data)

            decay_penalty = max(0, 1.0 - recency_mult)
            if decay_penalty > 0:
                # mapping recency decay to negative evidence to pull the score down if it's an old skill
                evidence.append(Evidence(source="Recency", confidence=conf["RECENCY"], strength=decay_penalty, is_negative=True))
            
            source_details.append({
                "source": "Temporal Audit",
                "score": -decay_penalty if decay_penalty > 0 else 1.0,
                "trust": conf["RECENCY"],
                "explanation": f"{recency_note} (Multiplier: {recency_mult:.2f})",
                "weighting": "Recency Check"
            })

            # --- Probabilistic Evidence Fusion ---
            fusion_result = self._fuse_evidence(evidence)
            final_item_score = fusion_result["fused_score"]
            conf_label = fusion_result["confidence_label"]
            
            # weakest source
            weakest_source = "None"
            min_impact = 99.0
            if evidence:
                for ev in evidence:
                    impact = ev.strength * ev.confidence
                    if impact < min_impact and not ev.is_negative:
                        min_impact = impact
                        weakest_source = ev.source

            # Summary for the UI
            if conf_label == "High Confidence":
                human_note = "Multi-source consensus achieved."
            elif conf_label == "Medium Confidence":
                human_note = "Skill verified across multiple professional profiles."
            elif conf_label == "No Evidence":
                human_note = "No verifiable records found for this technology."
            else:
                human_note = f"Inconsistent data. {weakest_source} verification is the primary bottleneck."

            total_item_score += final_item_score

            breakdown.append({
                "item": tech_display,

                "score": final_item_score,
                "uncertainty": fusion_result["uncertainty"],
                "confidence_label": conf_label,
                "confidence_reason": fusion_result.get("confidence_reason"),
                "bottleneck": weakest_source,
                "alpha": fusion_result["alpha"],
                "beta": fusion_result["beta"],
                "confidence_interval": fusion_result["confidence_interval"],
                "source_details": source_details,
                "notes": f"{human_note} (Bayesian Audit: {fusion_result['logic']})",
                "sources": list(set(item_sources))
            })

        final_score = total_item_score / len(target_tech) if target_tech else 0
        
        # determining technical formula
        if len(target_tech) == 1 and len(breakdown) == 1:
            tech_formula = breakdown[0]["notes"].replace("Logic: ", "")
        else:
            tech_formula = f"Avg({total_item_score:.2f} Total Points / {len(target_tech)} Items) = {final_score:.2f}"

        # --- Improvement Analysis ---
        improvements = []
        if final_score < 0.95:
            remaining = 1.0 - final_score
            
            # Source performance
            source_scores = {}
            for b in breakdown:
                for sd in b.get("source_details", []):
                    src = sd.get("source")
                    if src not in source_scores: source_scores[src] = []
                    source_scores[src].append(sd.get("score", 0))
            
            avg_sources = {k: sum(v)/len(v) for k, v in source_scores.items()}
            
            # Uncertainty Bottleneck
            any_uncertain = any(b.get("confidence_label") in ["Low Confidence", "Medium Confidence"] for b in breakdown)
            if any_uncertain:
                worst_src = min(avg_sources, key=avg_sources.get) if avg_sources else "CV"
                improvements.append({
                    "text": f"The model detected inconsistent evidence for your tech stack, primarily on the {worst_src} profile. Ensure your professional records are synchronised to reduce Beta (Uncertainty).",
                    "gain": remaining * 0.4,
                    "id": "BETA_UNCERTAINTY"
                })

            # Source-Specific Advice
            if avg_sources.get("LinkedIn", 1.0) < 0.8:
                improvements.append({
                    "text": "Your LinkedIn profile lacks explicit verification for several key technologies. Add these to your Skills section to improve cross-platform consensus.",
                    "gain": remaining * 0.3,
                    "id": "LI_CONSENSUS"
                })
            
            if avg_sources.get("GitHub", 1.0) < 0.7:
                improvements.append({
                    "text": "Increase your public code footprint for these technologies by contributing to relevant open-source projects or creating documented repositories.",
                    "gain": remaining * 0.2,
                    "id": "GH_FOOTPRINT"
                })
        else:
            improvements.append({"text": "Maximum technology stack score achieved across all requirements.", "gain": 0.0})

        return {
            "score": round(final_score, 2),
            "name": self.name,
            "id": self.id,
            "calculation_formula": "Bayesian_Fusion(CV_Presence, LI_Endorsement, GH_Project_Affinity)",
            "technical_formula": tech_formula,
            "breakdown": breakdown,
            "has_semantic_bridge": any(b.get("is_semantic_bridge") for b in breakdown),
            "sources_used": list(set([src for b in breakdown for src in b["sources"]])),
            "glossary": [
                {"term": "Alpha (α)", "definition": "Strength of supporting evidence across all sources."},
                {"term": "Beta (β)", "definition": "Level of contradictory or missing signals causing uncertainty."}
            ],
            "improvements": improvements[:2]
        }
