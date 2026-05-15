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
        Ensures that even enriched/cached metadata is wiped if the source is inactive.
        """
        masked = copy.deepcopy(candidate_data)
        
        # mapping of sources to their data keys and enriched metadata prefixes
        source_mapping = {
            "CV": {
                "keys": ["skills", "cv_experience", "projects_history", "extracurricular", 
                         "experience_summary", "raw_cv_text", "full_cv_text", "cv_education"],
                "prefixes": ["raw_cv_"]
            },
            "GitHub": {
                "keys": ["github_profile", "github_enriched", "github_projects"],
                "prefixes": ["raw_gh_"]
            },
            "LinkedIn": {
                "keys": ["linkedin_profile", "linkedin_enriched", "linkedin_experience", "linkedin_education"],
                "prefixes": ["raw_li_"]
            }
        }
        
        # also mask generic raw counts that might be derived from multiple sources
        generic_raw_keys = ["raw_tenure_months", "raw_skill_count", "raw_impact_points", "raw_repo_count", "raw_star_count", "raw_fork_count", "raw_connections"]
        
        for source, config in source_mapping.items():
            if source not in active_sources:
                # wipe raw keys
                for key in config["keys"]:
                    if key in masked:
                        masked[key] = [] if isinstance(masked[key], list) else ({} if isinstance(masked[key], dict) else None)
                
                # wipe prefixed metadata (e.g. raw_gh_complexity)
                for key in list(masked.keys()):
                    if any(key.startswith(p) for p in config["prefixes"]):
                        masked[key] = 0
        
        # if NO sources are active, wipe everything else that's derived
        if not active_sources:
            for key in generic_raw_keys:
                if key in masked:
                    masked[key] = 0
            # Also clear batch context to be safe
            for key in list(masked.keys()):
                if key.startswith("batch_"):
                    masked[key] = 0
                            
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
