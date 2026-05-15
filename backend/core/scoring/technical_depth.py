from typing import Dict, Any, List, Optional
from .base import BaseMetric

class TechnicalDepthMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "technical_depth"

    @property
    def name(self) -> str:
        return "Verified Technical Depth"

    @property
    def description(self) -> str:
        return "Evaluates the depth of technical expertise by cross-referencing CV claims with verifiable GitHub activity and project impact."

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Calculates technical depth by looking at skill overlap, 
        verifiable github activity, and general project impact."""
        breakdown = []
        sources_used = ["CV"]
        
        # Extract relevant technical skills from JD
        # Job metrics are stored as grouped_metrics: { "Technologies": {"type": "list", "value": [...]}, ... }
        jd_metrics = job_requirements.get("metrics", {})
        target_skills = set()
        for cat in ["Technologies", "Languages"]:
            if cat in jd_metrics:
                target_skills.update([s.lower() for s in jd_metrics[cat].get("value", [])])

        if not target_skills:
            return {
                "score": 0.0,
                "breakdown": [{"component": "Prerequisite", "score": 0.0, "notes": "No technical skills defined in job description."}],
                "sources_used": sources_used
            }

        # CV Skill Overlap
        cv_skills = [s.lower() for s in candidate_data.get("skills", [])]
        overlap = [s for s in cv_skills if s in target_skills]
        cv_score = len(overlap) / len(target_skills) if target_skills else 0
        breakdown.append({
            "component": "CV Skill Alignment",
            "score": cv_score,
            "notes": f"Matched {len(overlap)}/{len(target_skills)} required technical skills from CV."
        })

        # GitHub Verification
        gh_score = 0.0
        gh_profile = candidate_data.get("github_profile")
        if gh_profile:
            sources_used.append("GitHub")
            gh_languages = {l["label"].lower(): l["pct"] for l in gh_profile.get("languages", []) if "label" in l}
            
            # Check how many target skills are represented in GitHub languages
            verified_languages = [s for s in target_skills if s in gh_languages]
            if verified_languages:
                # Average percentage of usage for verified languages
                avg_pct = sum(gh_languages[s] for s in verified_languages) / len(verified_languages)
                # We normalise: if you have 100% of skills verified with high usage, you get 1.0
                # Removed the 0.5 baseline to ensure scores are purely proportional to verified density
                gh_score = (len(verified_languages) / len(target_skills)) * (avg_pct / 50.0)
                gh_score = self._normalise_score(gh_score)
                
            breakdown.append({
                "component": "GitHub Verification",
                "score": gh_score,
                "notes": f"Verified {len(verified_languages)} skills via public code repositories. Average usage density: {avg_pct:.1f}%" if verified_languages else "No required languages found in public GitHub repositories."
            })
        else:
            breakdown.append({
                "component": "GitHub Verification",
                "score": 0.0,
                "notes": "No GitHub profile associated with this candidate for verification."
            })

        # project impact (github stars/forks)
        impact_score = 0.0
        if gh_profile:
            total_stars = gh_profile.get("total_stars", 0)
            total_prs = gh_profile.get("total_prs", 0)
            
            # Simple logarithmic scale for stars (1 star = 0.1, 10 = 0.5, 100 = 0.8, 1000 = 1.0)
            import math
            if total_stars > 0:
                impact_score = min(1.0, math.log10(total_stars + 1) / 3.0)
            
            breakdown.append({
                "component": "Repository Impact",
                "score": impact_score,
                "notes": f"Candidate has {total_stars} stars and {total_prs} PR contributions across public projects."
            })

        # Weighted Final Score
        final_score = (cv_score * 0.4) + (gh_score * 0.4) + (impact_score * 0.2)
        
        improvements = []
        if final_score < 1.0:
            if cv_score < 1.0:
                improvements.append({"text": "Explicitly list all required technical skills in your CV to maximise baseline alignment.", "gain": (1.0 - cv_score) * 0.4, "variables": ["CV_Score"]})
            if gh_score < 1.0:
                improvements.append({"text": "Push public repositories using the required skills to increase verifiable GitHub code density.", "gain": (1.0 - gh_score) * 0.4, "variables": ["GH_Score"]})
            if impact_score < 1.0:
                improvements.append({"text": "Contribute to high-impact open-source projects to increase repository stars and PR counts.", "gain": (1.0 - impact_score) * 0.2, "variables": ["Impact_Score"]})
            if len(improvements) < 3:
                improvements.append({"text": "Ensure your public code directly reflects your claimed technical capabilities.", "gain": 0.05, "variables": ["GH_Score", "Impact_Score"]})
        if not improvements:
            improvements.append({"text": "Maximum technical depth score achieved.", "gain": 0.0, "variables": []})

        return {
            "score": self._normalise_score(final_score),
            "breakdown": breakdown,
            "sources_used": list(set(sources_used)),
            "improvements": improvements[:3]
        }
