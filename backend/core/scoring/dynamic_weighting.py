import math
import re
from typing import List, Dict, Any
from core.supabase import supabase

class WeightingEngine:
    """
    Core engine for calculating skill importance using a modified TF-IDF approach.
    It compares how often a skill is mentioned in the current JD vs how common it 
    is in our historical database (the 'market' baseline).
    """
    
    def __init__(self):
        self.corpus = []
        self._sync_corpus()

    def _sync_corpus(self):
        """Pulls previous job descriptions from Supabase to use as a comparison baseline."""
        # TODO: maybe use a search index later
        response = supabase.table("job_requirements").select("description").execute()
        if response.data:
            self.corpus = [d["description"] for d in response.data if d.get("description")]

    def _clean_and_tokenise(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r'\w+', text.lower())

    def calculate_weights(self, jd_text: str, skills: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Derives suggested 1-5 priority weights. 
        Higher weights go to skills that are either mentioned a lot in the JD 
        or are rare across the market (high 'scarcity').
        """
        if not jd_text or not skills:
            return {s: {"weight": 3.0, "reasoning": "Standard baseline."} for s in skills}

        tokens = self._clean_and_tokenise(jd_text)
        total_words = len(tokens)
        
        if total_words == 0:
            return {s: {"weight": 3.0, "reasoning": "Baseline (Empty JD)."} for s in skills}

        num_docs = len(self.corpus) + 1 # + 1s are because current job
        doc_frequencies = {s: 0 for s in skills}
        
        for s in skills:
            s_lower = s.lower()
            for desc in self.corpus:
                if s_lower in desc.lower():
                    doc_frequencies[s] += 1
            if s_lower in jd_text.lower():
                doc_frequencies[s] += 1

        results = {}
        for s in skills:
            s_lower = s.lower()
            
            # job intensity (how many times JD mentions the skill)
            mentions = jd_text.lower().count(s_lower)
            intensity = mentions / total_words
            
            # market scarcity (stored jobs in supabase)
            df = doc_frequencies[s]
            scarcity = math.log(num_docs / (1 + df)) + 1
            
            # significance of this metric
            raw_significance = intensity * scarcity
            
            results[s] = {
                "score": raw_significance,
                "tf": intensity,
                "idf": scarcity,
                "count": mentions,
                "df": df
            }

        # linear mapping to our 1.5 - 5.0 priority scale
        scores = [r["score"] for r in results.values()]
        min_s, max_s = min(scores), max(scores)
        s_range = max_s - min_s
        
        final_output = {}
        for s, data in results.items():
            # if all skills have the same significance, we default to the middle (3.0)
            scaled = 3.0
            if s_range > 0:
                # map the raw IR score to a 1.5 (low) to 5.0 (high) priority
                scaled = 1.5 + (data["score"] - min_s) / s_range * 3.5
            
            if data["idf"] > 1.8:
                reason = "Niche skill; high market scarcity increases importance."
            elif data["count"] > 2:
                reason = f"High intensity; mentioned {data['count']} times in this job."
            elif data["idf"] < 1.1:
                reason = "Common requirement; baseline significance."
            else:
                reason = "Balanced significance based on density and rarity."

            final_output[s] = {
                "weight": round(scaled, 1),
                "reasoning": reason,
                "math": {
                    "tf": round(data["tf"], 6),
                    "idf": round(data["idf"], 4),
                    "count": data["count"],
                    "df": data["df"],
                    "total_tokens": total_words,
                    "num_docs": num_docs,
                    "raw_score": round(data["score"], 6)
                }
            }

        return final_output
