import re
from typing import List, Dict, Any

class TraditionalATS:
    """
    replicates a naive baseline keyword-matching recruitment system
    used for comparative studies in the merit fyp
    """
    
    def __init__(self, job_description: Dict[str, Any]):
        self.jd = job_description
        self.keywords = []
        metrics = job_description.get("metrics", {})
        for cat in ["Technologies", "Languages"]:
            if cat in metrics:
                self.keywords.extend([k.lower() for k in metrics[cat].get("value", [])])
        
    def score_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        cv_text = cv_text.lower()
        
        keyword_hits = {}
        total_hits = 0
        for kw in self.keywords:
            count = len(re.findall(rf'\b{re.escape(kw)}\b', cv_text))
            if count > 0:
                keyword_hits[kw] = count
                total_hits += count
        
        total_years = 0
        exp_data = candidate_data.get("experience", [])
        if isinstance(exp_data, list):
            for exp in exp_data:
                if isinstance(exp, dict):
                    total_years += exp.get("years", 0)
            
        has_degree = 1.0 if any(d in cv_text for d in ["bsc", "msc", "degree", "university", "computer science"]) else 0.0
        
        score = (total_hits * 0.5) + (total_years * 0.3) + (has_degree * 0.2)
        
        return {
            "name": candidate_data.get("name"),
            "score": round(score, 2),
            "total_years": total_years,
            "has_degree": "Yes" if has_degree > 0 else "No",
            "hits": total_hits
        }
