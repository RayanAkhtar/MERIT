from core.supabase import supabase
from core.scoring.registry import scoring_registry
import json

candidate_id = "7570a4a6-c712-4ded-8cb0-029e3b2e14fd"
candidate = supabase.table("candidate_data").select("*").eq("id", candidate_id).execute().data[0]

job_reqs = {
    "title": "Python Developer",
    "metrics": {
        "Languages": {
            "value": [{"name": "Python", "weight": 5}]
        }
    }
}

active_metrics = {"req_python": True}
weights = {"req_python": 1.0}

results = scoring_registry.run_all(candidate, job_reqs, active_metrics, weights)

print(f"\nFinal Overall Score: {results['overall_score']}")
print(f"Integrity Penalty: {results['calculation_summary']['integrity_penalty']}")
print(f"Flagged Terms: {results['calculation_summary']['stuffing_audit']}")
