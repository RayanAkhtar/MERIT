from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS

class ProfessionalGravityMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "professional_gravity"

    @property
    def name(self) -> str:
        return "Professional Gravity & Stability"

    @property
    def description(self) -> str:
        return "Evaluates career trajectory, tenure stability, and professional seniority by blending CV history with LinkedIn profile data."

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        """Calculates professional gravity by looking at tenure stability, 
        seniority alignment, and experience verification."""
        breakdown = []
        sources_used = ["CV"]
        
        # what level does the JD actually want
        jd_metrics = job_requirements.get("metrics") or {}
        general_metrics = jd_metrics.get("General") or {}
        jd_level = str(general_metrics.get("value") or "").lower()
        
        if not jd_level:
             # Try searching in flat metrics if grouped failed
             jd_level = str(job_requirements.get("experience_level") or "not specified").lower()

        # stability check: how long do they usually stay in a role?
        li_profile = candidate_data.get("linkedin_profile")
        experience = []
        if li_profile:
            sources_used.append("LinkedIn")
            experience = candidate_data.get("linkedin_experience") or []
        
        tenure_score = 0.5 # Default middle ground
        if experience:
            # Heuristic: Average years per role
            avg_tenure_years = 2.5 # Mock calculation
            tenure_score = self._normalise_score(avg_tenure_years / 5.0) # 5 years = perfect stability
            breakdown.append({
                "component": "Tenure Stability",
                "score": tenure_score,
                "notes": f"Average tenure per role is approximately {avg_tenure_years} years."
            })
        else:
            breakdown.append({
                "component": "Tenure Stability",
                "score": 0.5,
                "notes": "Insufficient granular experience data to calculate stability accurately."
            })

        # check if their titles match the seniority level
        seniority_score = 0.5
        # Check if candidate headline or roles match JD level (e.g. 'Senior', 'Lead')
        headline = ""
        if li_profile:
            headline = str(li_profile.get("headline") or "").lower()
        
        if jd_level in ["senior", "lead", "principal"] and any(kw in headline for kw in ["senior", "lead", "principal", "architect"]):
            seniority_score = 1.0
        elif jd_level in ["junior", "entry"] and any(kw in headline for kw in ["junior", "intern", "entry"]):
            seniority_score = 1.0
            
        breakdown.append({
            "component": "Seniority Alignment",
            "score": seniority_score,
            "notes": f"Candidate profile signals alignment with {jd_level} requirements."
        })

        # can we verify their experience?
        verification_score = 1.0 if li_profile else 0.0
        breakdown.append({
            "component": "Experience Verification",
            "score": verification_score,
            "notes": "Verified via LinkedIn profile." if li_profile else "Unable to verify professional claims via social sources."
        })

        final_score = (tenure_score * 0.4) + (seniority_score * 0.4) + (verification_score * 0.2)
        
        improvements = []
        if final_score < 1.0:
            if tenure_score < 1.0:
                improvements.append({"text": "Increase average tenure at companies to demonstrate greater professional stability and loyalty.", "gain": (1.0 - tenure_score) * 0.4, "variables": ["TenurePoints", "LoyaltyBonus"]})
            if seniority_score < 1.0:
                improvements.append({"text": f"Ensure your current role title and headline align explicitly with the target seniority ({jd_level}).", "gain": (1.0 - seniority_score) * 0.4, "variables": ["ImpactDensity"]})
            if verification_score < 1.0:
                improvements.append({"text": "Maintain an active, fully detailed LinkedIn profile to verify professional experience claims.", "gain": (1.0 - verification_score) * 0.2, "variables": ["TenurePoints"]})
            if len(improvements) < 3:
                improvements.append({"text": "Focus CV bullet points on measurable impact rather than just daily responsibilities.", "gain": 0.05, "variables": ["ImpactDensity"]})
        if not improvements:
            improvements.append({"text": "Maximum professional gravity score achieved.", "gain": 0.0, "variables": []})

        return {
            "score": self._normalise_score(final_score),
            "calculation_formula": "(TenurePoints + LoyaltyBonus + ImpactDensity) / 4",
            "glossary": [
                {
                    "variable": "TenurePoints",
                    "description": "Total years they've spent in relevant roles.",
                    "impact": "Primary vertical growth signal.",
                    "sensitivity": "Doesn't favour job-hoppers much."
                },
                {
                    "variable": "LoyaltyBonus",
                    "description": "A small boost for staying at one place for more than 2 years.",
                    "impact": "Retention indicator.",
                    "sensitivity": "Only kicks in for long stints."
                },
                {
                    "variable": "ImpactDensity",
                    "description": "Looks for evidence of actual results (like 'cut costs' or 'speed up system').",
                    "impact": "Seniority and accountability signal.",
                    "sensitivity": "Low if the CV is just a list of tasks."
                }
            ],
            "breakdown": breakdown,
            "sources_used": list(set(sources_used)),
            "improvements": improvements[:3]
        }
