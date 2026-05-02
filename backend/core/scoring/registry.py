from typing import Dict, Any, List, Optional
import re
from .base import BaseMetric
from .language_expertise import LanguageExpertiseMetric
from .technology_stack import TechnologyStackMetric
from .education_metric import EducationMetric
from .soft_skills_metric import SoftSkillsMetric
from .professional_gravity import ProfessionalGravityMetric
from .intelligence_metrics import (
    ExperienceMetric, ProjectsMetric, TechSkillsMetric,
    GithubComplexityMetric, GithubAlignmentMetric, GithubImpactMetric,
    LinkedinExtracurricularMetric, LinkedinNetworkMetric
)

class ScoringRegistry:
    def __init__(self):
        self.metric_templates: Dict[str, BaseMetric] = {}
        # Register core templates
        self.register(LanguageExpertiseMetric())
        self.register(TechnologyStackMetric())
        self.register(EducationMetric())
        self.register(SoftSkillsMetric())
        self.register(ProfessionalGravityMetric())
        
        # Register Intelligence Metrics
        self.register(ExperienceMetric())
        self.register(ProjectsMetric())
        self.register(TechSkillsMetric())
        self.register(GithubComplexityMetric())
        self.register(GithubAlignmentMetric())
        self.register(GithubImpactMetric())
        self.register(LinkedinExtracurricularMetric())
        self.register(LinkedinNetworkMetric())

    def register(self, metric: BaseMetric):
        self.metric_templates[metric.id] = metric

    def _get_metric_for_key(self, key: str, job_requirements: Dict[str, Any]) -> Optional[BaseMetric]:
        """
        Determines which metric template should handle a specific config key.
        """
        # check for a direct match first
        if key in self.metric_templates:
            return self.metric_templates[key]
        
        # requirement keys (e.g. 'req_python', 'req_AWS')
        if key.startswith("req_"):
            # Try to find which category this requirement belongs to in the JD
            clean_name = key.replace("req_", "").replace("_", " ").lower()
            jd_metrics = job_requirements.get("metrics", {})
            
            # Check Languages
            langs = [l.lower() for l in jd_metrics.get("Languages", {}).get("value", [])]
            if clean_name in langs:
                return self.metric_templates.get("languages")
            
            # Check Technologies
            techs = [t.lower() for t in jd_metrics.get("Technologies", {}).get("value", [])]
            if any(clean_name in t.lower() or t.lower() in clean_name for t in techs):
                return self.metric_templates.get("technologies")
            
            # Check Soft Skills
            soft = [s.lower() for s in jd_metrics.get("Soft Skills", {}).get("value", [])]
            if any(clean_name in s.lower() or s.lower() in clean_name for s in soft):
                return self.metric_templates.get("soft_skills")
                
            # Default to tech stack if unknown requirement
            return self.metric_templates.get("technologies")

        return None

    def run_all(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], 
                active_metrics: Optional[Dict[str, bool]] = None, weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Runs all active metrics and maps them to the provided weights.
        """
        results = {}
        total_weighted_score = 0.0
        total_weight = 0.0

        # Handle active_metrics as a dict (as provided in user example)
        if isinstance(active_metrics, dict):
            keys_to_run = [k for k, v in active_metrics.items() if v is True]
        else:
            # Fallback for list-based active_metrics
            keys_to_run = active_metrics if active_metrics else list(self.metric_templates.keys())

        if not keys_to_run:
            return {
                "overall_score": 0.0, 
                "metrics": {}, 
                "sources_used": [],
                "calculation_summary": {
                    "weighted_sum": 0,
                    "total_weight": 0,
                    "formula": "N/A",
                    "logic": "No active metrics selected."
                }
            }

        for key in keys_to_run:
            metric = self._get_metric_for_key(key, job_requirements)
            if not metric:
                # If no handler, we skip or provide a zero score
                continue
                
            # Determine "active_items" for the metric if it's a specific requirement
            active_items = None
            if key.startswith("req_"):
                # Pass the specific item to the metric
                clean_name = key.replace("req_", "").replace("_", " ")
                active_items = [clean_name]

            # Execute calculation
            # Note: We pass the specific key as context if needed
            res = metric.calculate(candidate_data, job_requirements, active_items=active_items)
            
            # Apply weight
            raw_weight = weights.get(key, 3.0) if weights else 3.0
            
            total_weighted_score += res["score"] * raw_weight
            total_weight += raw_weight
            
            # We use the 'key' from the config as the ID in the results for the frontend
            # Merge everything from res, ensuring we don't overwrite crucial keys
            merged_res = {**res}
            merged_res.update({
                "name": active_items[0] if active_items else metric.name,
                "weight": raw_weight,
                "score": res["score"],
                "formula": res.get("calculation_formula", "Simple Weighted Average"),
                "technical_formula": res.get("technical_formula", ""),
                "glossary": res.get("glossary", []),
                "breakdown": res.get("breakdown", []),
                "sources_used": res.get("sources_used", []),
                "improvements": res.get("improvements", [])
            })
            results[key] = merged_res

        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0

        return {
            "overall_score": overall_score,
            "calculation_summary": {
                "formula": "SUM(MetricScore * Weight) / SUM(Weights)",
                "weighted_sum": total_weighted_score,
                "total_weight": total_weight,
                "logic": f"Final Match % = ({total_weighted_score:.2f} weighted points) / ({total_weight:.1f} max weight points)"
            },
            "metrics": results
        }

# Global instance
scoring_registry = ScoringRegistry()
