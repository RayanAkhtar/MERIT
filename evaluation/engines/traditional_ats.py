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
        
        # check both top-level JD keys and nested metrics for skill lists
        sources = [job_description, job_description.get("metrics", {})]
        skill_keys = ["Technologies", "Languages", "Technical Skills", "technical_skills", "languages"]
        
        for source in sources:
            for cat in skill_keys:
                val = source.get(cat, {})
                if isinstance(val, dict):
                    self.keywords.extend([str(k).lower() for k in val.get("value", [])])
                elif isinstance(val, list):
                    self.keywords.extend([str(k).lower() for k in val])
        
        # deduplicate
        self.keywords = list(set(self.keywords))
        
    def score_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        cv_text = cv_text.lower()
        
        # binary keyword matching: does the CV contain this keyword? yes/no
        # real ATS systems check presence, not frequency
        keyword_hits = {}
        matched_count = 0
        for kw in self.keywords:
            present = bool(re.search(rf'\b{re.escape(kw)}\b', cv_text))
            if present:
                keyword_hits[kw] = 1
                matched_count += 1
        
        # keyword match ratio (0.0 to 1.0)
        match_ratio = matched_count / len(self.keywords) if self.keywords else 0.0
        
        total_years = 0
        exp_data = candidate_data.get("experience", [])
        if isinstance(exp_data, list):
            for exp in exp_data:
                if isinstance(exp, dict):
                    total_years += exp.get("years", 0)
        elif isinstance(exp_data, str):
            # fallback: simple heuristic for years if it's a block of text
            # count date patterns like "2021 - 2024" or "Jan 2024 - Apr 2024"
            date_matches = re.findall(r'\b(20\d{2})\b', exp_data)
            if date_matches:
                years = [int(y) for y in date_matches]
                total_years = max(0, max(years) - min(years))
            else:
                # very crude fallback: assume 1 year per 500 chars of experience text
                total_years = len(exp_data) / 500.0
            
        has_degree = 1.0 if any(d in cv_text for d in ["bsc", "msc", "degree", "university", "computer science"]) else 0.0
        
        # simple weighted score: keyword presence + years + education
        score = (match_ratio * 5.0) + (total_years * 0.3) + (has_degree * 0.2)
        
        return {
            "name": candidate_data.get("name"),
            "score": round(score, 2),
            "total_years": total_years,
            "has_degree": "Yes" if has_degree > 0 else "No",
            "hits": matched_count
        }
