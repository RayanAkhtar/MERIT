"""Offline TF-IDF weighting for Study 13 (injectable market corpus, no Supabase)."""
from __future__ import annotations

import math
import re
from typing import Any, Dict, List


class OfflineWeightingEngine:
    def __init__(self, corpus: List[str]):
        self.corpus = [d for d in corpus if d]

    def _clean_and_tokenise(self, text: str) -> List[str]:
        if not text:
            return []
        return re.findall(r"\w+", text.lower())

    def calculate_weights(self, jd_text: str, skills: List[str]) -> Dict[str, Dict[str, Any]]:
        if not jd_text or not skills:
            return {s: {"weight": 3.0, "reasoning": "Standard baseline."} for s in skills}

        tokens = self._clean_and_tokenise(jd_text)
        total_words = len(tokens)
        if total_words == 0:
            return {s: {"weight": 3.0, "reasoning": "Baseline (Empty JD)."} for s in skills}

        num_docs = len(self.corpus) + 1
        doc_frequencies = {s: 0 for s in skills}

        for s in skills:
            s_lower = s.lower()
            for desc in self.corpus:
                if s_lower in desc.lower():
                    doc_frequencies[s] += 1
            if s_lower in jd_text.lower():
                doc_frequencies[s] += 1

        results: Dict[str, Dict[str, Any]] = {}
        for s in skills:
            s_lower = s.lower()
            mentions = jd_text.lower().count(s_lower)
            intensity = mentions / total_words
            df = doc_frequencies[s]
            scarcity = math.log(num_docs / (1 + df)) + 1
            raw_significance = intensity * scarcity
            results[s] = {
                "score": raw_significance,
                "tf": intensity,
                "idf": scarcity,
                "count": mentions,
                "df": df,
            }

        scores = [r["score"] for r in results.values()]
        min_s, max_s = min(scores), max(scores)
        s_range = max_s - min_s

        # Same [1.0, 5.0] significance band as backend/core/scoring/dynamic_weighting.py
        final_output: Dict[str, Dict[str, Any]] = {}
        for s, data in results.items():
            scaled = 3.0
            if s_range > 0:
                scaled = 1.0 + (data["score"] - min_s) / s_range * 4.0

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
                    "raw_score": round(data["score"], 6),
                },
            }

        return final_output
