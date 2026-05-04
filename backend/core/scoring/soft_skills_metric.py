from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS

class SoftSkillsMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "soft_skills"

    @property
    def name(self) -> str:
        return "Behavioural & Soft Skills"

    @property
    def description(self) -> str:
        # Looking at summary and about sections to find behavioural indicators. 
        # It's a bit limited but gives a good hint of personality.
        return "Analyses interpersonal and behavioural indicators from the CV profile summary and LinkedIn 'About' sections."

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        breakdown = []
        sources_used = ["CV"]
        
        # get soft skills from JD (assuming they are in the 'Soft Skills' category)
        # print(f"DEBUG - soft_reqs: {soft_reqs}")
        jd_metrics = job_requirements.get("metrics", {})
        soft_reqs = jd_metrics.get("Soft Skills", {}).get("value", [])
        
        # extract narrative text for analysis (Safety: handle None)
        cv_summary = str(candidate_data.get("experience_summary") or "")
        li_about = ""
        li_profile = candidate_data.get("linkedin_profile")
        if li_profile:
            sources_used.append("LinkedIn")
            li_about = str(li_profile.get("about") or "")
            
        full_narrative = (cv_summary + " " + li_about).lower()
        
        # simple keyword analysis
        # print(f"checking {len(soft_reqs)} skills")
        total_item_score = 0.0
        for skill in soft_reqs:
            # handle dict or string
            skill_val = skill.get("value") if isinstance(skill, dict) else skill
            skill_lower = str(skill_val).lower()
            
            # Significance-based base score - I've set LinkedIn higher because 
            # people usually lie less on public profiles than on a private CV.
            item_sources = []
            source_details = []
            
            if skill_lower in li_about.lower():
                item_sources.append("LinkedIn")
                start_idx = max(0, li_about.lower().find(skill_lower) - 40)
                end_idx = min(len(li_about), li_about.lower().find(skill_lower) + 60)
                snippet = li_about[start_idx:end_idx].strip()
                source_details.append({
                    "source": "LinkedIn",
                    "score": 0.60,
                    "explanation": f"Narrative proof: \"...{snippet}...\"",
                    "weighting": "Social profile verification"
                })

            if skill_lower in cv_summary.lower():
                item_sources.append("CV")
                start_idx = max(0, cv_summary.lower().find(skill_lower) - 40)
                end_idx = min(len(cv_summary), cv_summary.lower().find(skill_lower) + 60)
                snippet = cv_summary[start_idx:end_idx].strip()
                source_details.append({
                    "source": "CV",
                    "score": 0.40,
                    "explanation": f"Claimed in summary: \"...{snippet}...\"",
                    "weighting": "Self-reported narrative"
                })
            
            base_score = 0.60 if "LinkedIn" in item_sources else (0.40 if "CV" in item_sources else 0.15)
            item_score = self._calculate_multi_source_bonus(item_sources, base_score)
            total_item_score += item_score
            
            breakdown.append({
                "item": skill,
                "score": item_score,
                "source_details": source_details,
                "notes": f"Verification Reward applied via cross-narrative evidence." if len(item_sources) > 1 else "Single source identification.",
                "sources": list(set(item_sources)) if item_sources else ["CV"]
            })

        # If there are no reqs, just give a baseline of 0.5 so they don't get 0
        final_score = total_item_score / len(soft_reqs) if soft_reqs else 0.5
        
        improvements = []
        if final_score < 1.0:
            remaining = 1.0 - final_score
            avg_cv = sum(1 for b in breakdown if "CV" in b["sources"]) / len(breakdown) if breakdown else 0
            avg_li = sum(1 for b in breakdown if "LinkedIn" in b["sources"]) / len(breakdown) if breakdown else 0

            if avg_cv < 1.0:
                improvements.append({"text": "Weave required behavioural traits directly into the CV professional summary.", "gain": remaining * 0.4, "variables": ["SkillScore"]})
            if avg_li < 1.0:
                improvements.append({"text": "Include specific soft skill keywords in your LinkedIn 'About' section for multi-source verification.", "gain": remaining * 0.3, "variables": ["SkillScore"]})
            
            improvements.append({"text": "Provide explicit narrative proof of leadership or communication rather than just listing the words.", "gain": remaining * 0.3, "variables": ["SkillScore"]})
            
            if not improvements:
                improvements.append({"text": "Ensure your soft skills perfectly align with the job description requirements.", "gain": remaining, "variables": []})
        else:
            improvements.append({"text": "Maximum behavioural score achieved.", "gain": 0.0, "variables": []})

        return {
            "score": self._normalise_score(final_score),
            "calculation_formula": "Average(IndividualSkillScores)",
            "glossary": [
                {
                    "variable": "SkillScore",
                    "description": "Binary keyword match for behavioural traits (e.g., 'Leadership', 'Agile').",
                    "impact": "Averages across all requested soft skills.",
                    "sensitivity": "Low if behavioural keywords are missing from the CV summary."
                }
            ],
            "breakdown": breakdown,
            "sources_used": list(set(sources_used)),
            "improvements": improvements[:3]
        }
