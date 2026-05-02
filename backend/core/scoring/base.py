from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

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
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Does the actual scoring. Returns a dict with the score (0-1), 
        a breakdown of how it was reached, and some improvement tips.
        """
        pass

    def _normalise_score(self, score: float) -> float:
        """Ensures score is between 0 and 1"""
        return max(0.0, min(1.0, score))

    def _calculate_multi_source_bonus(self, found_sources: List[str], base_score: float) -> float:
        """
        Apply a little bonus if the skill is found in multiple places (e.g. CV and LinkedIn).
        Using a 1.15x multiplier for now.
        """
        if not found_sources:
            return 0.0
            
        # If more than 1 source (e.g. CV + GitHub), apply 1.15x multiplier
        multiplier = 1.15 if len(set(found_sources)) > 1 else 1.0
        return self._normalise_score(base_score * multiplier)
