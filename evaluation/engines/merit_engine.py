import sys
import os
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from core.scoring.registry import scoring_registry

class MeritEngine:
    """
    wrapper for the merit recruitment engine to be used in comparative studies
    can be toggled between cv-only (ablation) and multi-source (full) modes
    """
    
    def __init__(self, job_description: Dict[str, Any], cv_only: bool = False, explainable: bool = False):
        self.jd = job_description
        self.cv_only = cv_only
        self.explainable = explainable
        self.active_metrics = {}
        self.weights = {}
        self._prepare_metrics()

    def _prepare_metrics(self):
        jd_metrics = self.jd.get("metrics", {})
        
        # dynamic tech/lang metrics
        for cat in ["Technologies", "Languages"]:
            if cat in jd_metrics:
                weight = jd_metrics[cat].get("weight", 0.7)
                for item in jd_metrics[cat].get("value", []):
                    key = f"req_{item.lower().replace(' ', '_')}"
                    self.active_metrics[key] = True
                    self.weights[key] = weight

        # standard merit metrics
        self.active_metrics["experience"] = True
        self.weights["experience"] = jd_metrics.get("Experience", {}).get("weight", 0.4)
        
        self.active_metrics["projects"] = True
        self.weights["projects"] = 0.5
        
        self.active_metrics["professional_gravity"] = True
        self.weights["professional_gravity"] = 0.2
        
        self.active_metrics["education"] = True
        self.weights["education"] = jd_metrics.get("Education", {}).get("weight", 0.4)

    def score_candidate(self, candidate_data: Dict[str, Any], include_audit: bool = False) -> Dict[str, Any]:
        """
        evaluates a candidate and returns a dictionary of results.
        if include_audit is true, it attaches the full bayesian audit trail.
        """
        cand = candidate_data.copy()
        if self.cv_only:
            cand["github_enriched"] = None
            cand["linkedin_enriched"] = None
            cand["linkedin_experience"] = []
            
        if "experience" in cand and isinstance(cand["experience"], list):
            if "full_cv_text" not in cand:
                exp_text = " ".join([str(e.get("description", "")) for e in cand["experience"]])
                skills_text = ", ".join(cand.get("skills", []))
                cand["full_cv_text"] = f"{cand.get('summary', '')} {exp_text} {skills_text}"

        # run merit scoring
        scored_data = scoring_registry.run_all(
            cand,
            self.jd, 
            self.active_metrics, 
            self.weights
        )
        
        res = {
            "name": cand["name"],
            "score": round(scored_data["overall_score"] * 100, 2)
        }
        
        if include_audit or self.explainable:
            res["metrics"] = scored_data["metrics"]
            
            if self.explainable:
                from core.scoring.explainability import ShapleyExplainer
                explainer = ShapleyExplainer(scoring_registry)
                res["shapley"] = explainer.calculate_contributions(cand, self.jd, self.active_metrics, self.weights)
        
        return res
