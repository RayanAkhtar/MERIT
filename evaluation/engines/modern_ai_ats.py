import sys
import os
import re
from typing import List, Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from core.scoring.semantic_utils import semantic_matcher

class SemanticATSModel:
    """
    replicates a modern ai-powered ats using semantic embeddings
    used for comparative studies to show how even 'smart' systems can be fooled
    """
    
    def __init__(self, job_description: Dict[str, Any]):
        self.jd = job_description
        self.target_skills = []
        
        # check both top-level JD keys and nested metrics for skill lists
        sources = [job_description, job_description.get("metrics", {})]
        skill_keys = ["Technologies", "Languages", "Technical Skills", "technical_skills", "languages"]
        
        for source in sources:
            for cat in skill_keys:
                val = source.get(cat, {})
                if isinstance(val, dict):
                    self.target_skills.extend([str(k).lower() for k in val.get("value", [])])
                elif isinstance(val, list):
                    self.target_skills.extend([str(k).lower() for k in val])
        
        self.target_skills = list(set(self.target_skills))
                
    def score_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        cv_chunks = [chunk.strip() for chunk in cv_text.replace('.', '\n').split('\n') if len(chunk.strip()) > 5]
        
        if not cv_chunks:
            cv_chunks = [cv_text]
            
        semantic_hits = {}
        total_semantic_score = 0.0
        
        for skill in self.target_skills:
            match_result = semantic_matcher.find_best_match(skill, cv_chunks, threshold=0.55)
            if match_result["match"]:
                score = match_result["score"]
                semantic_hits[skill] = round(score, 2)
                total_semantic_score += score
            else:
                semantic_hits[skill] = 0.0
                
        total_years = 0
        exp_data = candidate_data.get("experience", [])
        if isinstance(exp_data, list):
            for exp in exp_data:
                if isinstance(exp, dict):
                    total_years += exp.get("years", 0)
        elif isinstance(exp_data, str):
            date_matches = re.findall(r'\b(20\d{2})\b', exp_data)
            if date_matches:
                years = [int(y) for y in date_matches]
                total_years = max(0, max(years) - min(years))
            else:
                total_years = len(exp_data) / 500.0
            
        jd_min_years = self.jd.get("metrics", {}).get("Experience", {}).get("min_years", 5)
        normalised_years = min(1.0, total_years / jd_min_years) if jd_min_years > 0 else 1.0
            
        final_score = (total_semantic_score * 0.7) + (normalised_years * 0.3 * 10) 
        
        return {
            "name": candidate_data.get("name"),
            "score": round(final_score, 2),
            "semantic_matches": semantic_hits,
            "total_years": total_years
        }
