from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from core.fusion.bayesian import BayesianEvidenceFusion, Evidence

class BaseMetric(ABC):
    """
    Base class for all metrics. Every metric needs an ID, name and a calculate method.
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for the metric category (e.g. 'languages')"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the metric"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description of what this metric evaluates"""
        pass

    @abstractmethod
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """
        Does the actual scoring. Returns a dict with the score (0-1), 
        a breakdown of how it was reached, and some improvement tips.
        """
        pass

    def _normalise_score(self, score: float) -> float:
        """Ensures score is between 0 and 1"""
        return max(0.0, min(1.0, score))

    def _fuse_evidence(self, evidence_list: List[Evidence]) -> Dict[str, Any]:
        """
        Helper to run Bayesian Evidence Fusion.
        """
        from core.scoring.constants import SCORING_CONSTANTS
        conf = SCORING_CONSTANTS["FUSION"]
        
        fusion = BayesianEvidenceFusion(
            prior_alpha=conf["PRIORS"]["ALPHA"],
            prior_beta=conf["PRIORS"]["BETA"],
            high_threshold=conf["THRESHOLDS"]["HIGH"],
            medium_threshold=conf["THRESHOLDS"]["MEDIUM"]
        )
        return fusion.fuse(evidence_list)
