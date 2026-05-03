import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Evidence:
    # simple container for source data
    source: str           # e.g., "CV", "GitHub"
    confidence: float     # how much we trust this source (0 to 1)
    strength: float       # how strong the skill signal is (0 to 1)
    is_negative: bool = False  # for things like skill decay

class BayesianEvidenceFusion:
    """
    I'm using a Beta distribution to model the candidate's competence.
    Alpha represents 'success' signals (evidence they have the skill), 
    and Beta represents 'failure' or noise (uncertainty or contradictions).
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0, high_threshold: float = 0.15, medium_threshold: float = 0.25):
        # Prior so we don't bias the results before seeing data
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.high_threshold = high_threshold
        self.medium_threshold = medium_threshold

    def fuse(self, evidence_list: List[Evidence]) -> Dict[str, Any]:
        # if there's no data, we just return a zero score
        if not evidence_list:
            return {
                "fused_score": 0.0,
                "uncertainty": 1.0, 
                "confidence_label": "No Evidence",
                "confidence_interval": (0.0, 0.0),
                "alpha": self.prior_alpha,
                "beta": self.prior_beta,
                "logic": "No evidence provided. Returning zero baseline."
            }

        alpha = self.prior_alpha
        beta = self.prior_beta

        for ev in evidence_list:
            # We update alpha and beta based on the strength of the signal and our trust in the source
            
            if ev.is_negative:
                # things like old experience increase beta directly
                beta += ev.strength * ev.confidence
                # add a tiny bit of noise to alpha based on source uncertainty
                alpha += (1.0 - ev.confidence) * 0.05
            else:
                # for positive evidence:
                # high strength + high confidence = big boost to alpha
                # low strength + high confidence = big boost to beta (meaning they probably don't have it)
                alpha += ev.strength * ev.confidence
                beta += (1.0 - ev.strength) * ev.confidence
                
                # add some residual noise so the model isn't too 'certain' if the source is shaky
                alpha += (1.0 - ev.confidence) * 0.01
                beta += (1.0 - ev.confidence) * 0.01

        # The mean of a Beta distribution is a / (a + b)
        fused_score = alpha / (alpha + beta)
        variance = self._calculate_variance(alpha, beta)
        std_dev = math.sqrt(variance)
        
        # work out a human-friendly label based on the standard deviation
        if std_dev < self.high_threshold:
            conf_label = "High Confidence"
        elif std_dev < self.medium_threshold:
            conf_label = "Medium Confidence"
        else:
            conf_label = "Low Confidence"

        # 95% confidence interval approximation (mean +/- 1.96 * std_dev)
        ci_low = max(0.0, fused_score - 1.96 * std_dev)
        ci_high = min(1.0, fused_score + 1.96 * std_dev)

        return {
            "fused_score": fused_score,
            "uncertainty": std_dev,
            "confidence_label": conf_label,
            "confidence_interval": (ci_low, ci_high),
            "alpha": alpha,
            "beta": beta,
            "logic": f"α (Success Signal) = {alpha:.2f}, β (Conflict/Noise) = {beta:.2f}. Calculated via: Prior + Sum(Strength * Trust)."
        }

    def _calculate_variance(self, a: float, b: float) -> float:
        # standard variance formula for Beta(a, b)
        return (a * b) / ((a + b)**2 * (a + b + 1))

    def _calculate_ci(self, a: float, b: float) -> tuple[float, float]:
        """Calculates a simple 95% CI approximation"""
        mean = a / (a + b)
        std_dev = math.sqrt(self._calculate_variance(a, b))
        return (max(0.0, mean - 1.96 * std_dev), min(1.0, mean + 1.96 * std_dev))
