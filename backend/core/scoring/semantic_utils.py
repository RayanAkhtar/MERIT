import torch
from sentence_transformers import SentenceTransformer, util
import os

class SemanticMatcher:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticMatcher, cls).__new__(cls)
            # using a lightweight model that offers best 'class separation' for tech terms
            # 'all-MiniLM-L6-v2' is superior at distinguishing between different languages
            model_name = 'all-MiniLM-L6-v2'
            try:
                cls._model = SentenceTransformer(model_name)
            except Exception as e:
                print(f"CRITICAL [Semantic]: Failed to load model: {str(e)}")
        return cls._instance

    def find_best_match(self, target: str, candidates: list, threshold: float = 0.6) -> dict:
        """
        finds the best semantic match in a list of candidates using pure vector similarity.
        threshold is set to 0.60 to handle technical terminology variances.
        """
        if not self._model or not target or not candidates:
            return {"match": None, "best_candidate": None, "score": 0.0}

        # Pure semantic matching: Clean strings but no artificial prefixes
        target_clean = target.lower().strip()
        candidates_clean = [c.lower().strip() for c in candidates]

        # 1. Exact match check (Efficiency)
        if target_clean in candidates_clean:
            idx = candidates_clean.index(target_clean)
            return {"match": candidates[idx], "best_candidate": candidates[idx], "score": 1.0}

        # 2. Vector Similarity
        target_emb = self._model.encode(target_clean, convert_to_tensor=True)
        cand_embs = self._model.encode(candidates_clean, convert_to_tensor=True)

        # compute all similarities at once
        cosine_scores = util.cos_sim(target_emb, cand_embs)[0]
        
        best_score = 0.0
        best_match_idx = 0
        
        for i, score in enumerate(cosine_scores):
            s = float(score)
            if s > best_score:
                best_score = s
                best_match_idx = i

        best_match = candidates[best_match_idx] if candidates else None

        return {
            "match": best_match if best_score >= threshold else None,
            "best_candidate": best_match,
            "score": best_score
        }

# singleton instance for easy access
semantic_matcher = SemanticMatcher()
