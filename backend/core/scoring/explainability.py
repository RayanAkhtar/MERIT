import copy
from typing import Dict, Any, List, Optional
import math

class ShapleyExplainer:
    """
    Implements Explainable AI (XAI) using Shapley Values from Cooperative Game Theory.
    Attributes the final match score to three primary data sources: CV, GitHub, and LinkedIn.
    """
    
    def __init__(self, scoring_registry):
        self.registry = scoring_registry
        self.sources = ["CV", "GitHub", "LinkedIn"]

    def _mask_candidate_data(self, candidate_data: Dict[str, Any], active_sources: List[str]) -> Dict[str, Any]:
        """
        Returns a copy of candidate_data with only the active sources' data remaining.
        """
        masked = copy.deepcopy(candidate_data)
        
        # mapping of sources to their data keys in the candidate object
        source_mapping = {
            "CV": [
                "skills", "cv_experience", "projects_history", "extracurricular", 
                "experience_summary", "raw_cv_text", "full_cv_text", "cv_education"
            ],
            "GitHub": ["github_profile", "github_enriched", "github_projects"],
            "LinkedIn": ["linkedin_profile", "linkedin_enriched", "linkedin_experience", "linkedin_education"]
        }
        
        for source, keys in source_mapping.items():
            if source not in active_sources:
                for key in keys:
                    if key in masked:
                        if isinstance(masked[key], list):
                            masked[key] = []
                        elif isinstance(masked[key], dict):
                            masked[key] = {}
                        else:
                            masked[key] = None
                            
        return masked

    def calculate_contributions(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], 
                               active_metrics: Dict[str, bool], weights: Dict[str, float]) -> Dict[str, float]:
        """
        Calculates Shapley values for each source.
        Returns a dict: { "CV": val, "GitHub": val, "LinkedIn": val }
        """
        # define all 2^3 = 8 permutations (coalitions of sources)
        coalitions = [
            [],
            ["CV"],
            ["GitHub"],
            ["LinkedIn"],
            ["CV", "GitHub"],
            ["CV", "LinkedIn"],
            ["GitHub", "LinkedIn"],
            ["CV", "GitHub", "LinkedIn"]
        ]
        
        # calculate v(S) for each coalition
        v_overall = {}
        v_metrics = {} # { metric_key: { subset_key: score } }
        
        for coalition in coalitions:
            subset_key = tuple(sorted(coalition))
            masked_data = self._mask_candidate_data(candidate_data, coalition)
            
            res = self.registry.run_all(masked_data, job_requirements, active_metrics, weights)
            v_overall[subset_key] = res["overall_score"]
            
            for m_key, m_val in res["metrics"].items():
                if m_key not in v_metrics:
                    v_metrics[m_key] = {}
                v_metrics[m_key][subset_key] = m_val.get("score", 0.0)

        n = 3
        def compute_shapley(values_dict):
            contributions = {source: 0.0 for source in self.sources}
            for source in self.sources:
                contribution = 0.0
                for coalition in coalitions:
                    if source in coalition:
                        continue
                    
                    s_subset = tuple(sorted(coalition))
                    with_source = tuple(sorted(coalition + [source]))
                    
                    # marginal contribution
                    v_with = values_dict.get(with_source, 0.0)
                    v_without = values_dict.get(s_subset, 0.0)
                    marginal = v_with - v_without
                    
                    s_size = len(coalition)
                    weight = (math.factorial(s_size) * math.factorial(n - s_size - 1)) / math.factorial(n)
                    contribution += weight * marginal
                contributions[source] = contribution
            return contributions

        # calculate for overall score
        overall_shapley = compute_shapley(v_overall)
        
        # calculate for each metric
        metrics_shapley = {}
        for m_key, m_values in v_metrics.items():
            metrics_shapley[m_key] = compute_shapley(m_values)

        return {
            "overall": overall_shapley,
            "metrics": metrics_shapley
        }
