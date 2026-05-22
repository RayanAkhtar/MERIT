import math
import re
from typing import List, Dict, Any
from core.supabase import supabase

# Backend significance band for suggested_weight (not the recruiter Likert).
# Higher = more significant on this JD relative to other listed skills.
# UI maps to P-1..P-5 via round(6 - weight) in ConfigEditor (1 = essential).
SIGNIFICANCE_MIN = 1.0
SIGNIFICANCE_MAX = 5.0
SIGNIFICANCE_SPAN = SIGNIFICANCE_MAX - SIGNIFICANCE_MIN  # 4.0
SIGNIFICANCE_MID = 3.0


class WeightingEngine:
    """
    Core engine for calculating skill importance using a modified TF-IDF approach.
    It compares how often a skill is mentioned in the current JD vs how common it
    is in our historical database (the 'market' baseline).

    Outputs ``suggested_weight`` on [SIGNIFICANCE_MIN, SIGNIFICANCE_MAX], not recruiter
    Likert 1--5. The JD review UI inverts that band when showing priorities.
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
        Derives suggested_weight per skill (SIGNIFICANCE_MIN..SIGNIFICANCE_MAX).

        Higher values mean higher IR significance (TF x IDF), min-max normalised across
        the skills on this JD only. Recruiters see integer P-1..P-5 after UI mapping.
        """
        if not jd_text or not skills:
            return {s: {"weight": SIGNIFICANCE_MID, "reasoning": "Standard baseline."} for s in skills}

        tokens = self._clean_and_tokenise(jd_text)
        total_words = len(tokens)
        
        if total_words == 0:
            return {s: {"weight": SIGNIFICANCE_MID, "reasoning": "Baseline (Empty JD)."} for s in skills}

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

        # Min-max normalise raw scores across skills on THIS jd into [1.0, 5.0].
        # Higher suggested_weight = stronger relative emphasis on this posting; weakest
        # skill on the list -> 1.0 (maps to P-5), strongest -> 5.0 (maps to P-1) after
        # round(6 - weight) in ConfigEditor.
        scores = [r["score"] for r in results.values()]
        min_s, max_s = min(scores), max(scores)
        s_range = max_s - min_s

        final_output = {}
        for s, data in results.items():
            scaled = SIGNIFICANCE_MID
            if s_range > 0:
                scaled = SIGNIFICANCE_MIN + (data["score"] - min_s) / s_range * SIGNIFICANCE_SPAN
            
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
