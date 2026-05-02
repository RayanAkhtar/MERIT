import re
from typing import Dict, Any, List
from .constants import SCORING_CONSTANTS

class KeywordStuffingDetector:
    """
    detects 'keyword stuffing'—where people spam buzzwords to try and game the system.
    """
    
    def __init__(self):
        self.cfg = SCORING_CONSTANTS.get("ANTI_STUFFING", {
            "OCCURRENCE_LIMIT": 5,
            "DENSITY_THRESHOLD": 0.05,
            "PENALTY_PER_OCCURRENCE": 0.03,
            "MAX_TOTAL_PENALTY": 0.3
        })

    def analyze(self, cv_text: str, target_keywords: List[str]) -> Dict[str, Any]:
        """
        checks the cv text for too much repetition
        """
        if not cv_text or not target_keywords:
            return {"penalty": 0.0, "flagged_terms": [], "is_stuffed": False}

        cv_text_lower = cv_text.lower()
        # clean the text to work out the density
        words = re.findall(r'\w+', cv_text_lower)
        total_word_count = len(words)
        
        flagged_terms = []
        total_penalty = 0.0

        for keyword in target_keywords:
            keyword_lower = keyword.lower()
            # only match whole words so we don't mix up 'Java' and 'JavaScript'
            pattern = rf'\b{re.escape(keyword_lower)}\b'
            occurrences = len(re.findall(pattern, cv_text_lower))
            
            if occurrences <= 0:
                continue

            density = occurrences / total_word_count if total_word_count > 0 else 0
            
            is_stuffed = False
            reason = ""
            
            if occurrences > self.cfg["OCCURRENCE_LIMIT"]:
                is_stuffed = True
                reason = f"Excessive repetition ({occurrences} occurrences)"

            if is_stuffed:
                # take points off for every occurrence over the limit
                excess = occurrences - self.cfg["OCCURRENCE_LIMIT"]
                penalty = excess * self.cfg["PENALTY_PER_OCCURRENCE"]
                total_penalty += penalty
                
                flagged_terms.append({
                    "term": keyword,
                    "count": occurrences,
                    "density": f"{density:.1%}",
                    "reason": reason,
                    "penalty_contribution": round(penalty, 3)
                })

        # cap the penalty so we don't zero someone out completely
        final_penalty = min(total_penalty, self.cfg["MAX_TOTAL_PENALTY"])
        
        return {
            "penalty": round(final_penalty, 3),
            "flagged_terms": flagged_terms,
            "is_stuffed": len(flagged_terms) > 0
        }
