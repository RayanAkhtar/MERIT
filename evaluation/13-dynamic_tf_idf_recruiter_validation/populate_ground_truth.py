"""
Populate Study 13 human ground truth: pilot panel (2 recruiters + 2 peers), 3 holdouts.
Run: python populate_ground_truth.py
"""
from __future__ import annotations

import json
import os
import statistics
from datetime import datetime
from typing import Any, Dict, List

from priority_scale import tfidf_continuous_to_ui_priority

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JD_DIR = os.path.join(SCRIPT_DIR, "test_data", "job_descriptions")
GT_DIR = os.path.join(SCRIPT_DIR, "test_data", "ground_truth")

ACTIVE_HOLDOUTS = (
    "holdout_01_junior_frontend_react",
    "holdout_02_senior_ml_research",
    "holdout_04_lead_devops_platform",
)

# Aligned with Study~14: small mixed panel ($N=4$)
PANEL = [
    {
        "id": "R_1",
        "role": "recruiter",
        "label": "Professional Recruiter",
        "background": "Technical recruiter (software roles); same panel as Study~14.",
    },
    {
        "id": "R_2",
        "role": "recruiter",
        "label": "Professional Recruiter",
        "background": "In-house hiring contact from prior internship network.",
    },
    {
        "id": "P_1",
        "role": "peer",
        "label": "MEng Computing (Imperial)",
        "background": "Final-year; SWE internship, familiar with JD screening tasks.",
    },
    {
        "id": "P_2",
        "role": "peer",
        "label": "MEng Computing (Imperial)",
        "background": "Final-year; ML coursework and prior quant internship.",
    },
]

# UI Likert: 1 = highest priority, 5 = lowest (ConfigEditor.tsx)
RATINGS: Dict[str, Dict[str, Dict[str, int]]] = {
    "holdout_01_junior_frontend_react": {
        "JavaScript": {"R_1": 2, "R_2": 2, "P_1": 2, "P_2": 2},
        "TypeScript": {"R_1": 2, "R_2": 2, "P_1": 2, "P_2": 1},
        # Recruiters treat markup/API glue as baseline — not differentiators
        "HTML": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 3},
        "CSS": {"R_1": 5, "R_2": 5, "P_1": 4, "P_2": 4},
        "React": {"R_1": 1, "R_2": 1, "P_1": 1, "P_2": 1},
        "Jest": {"R_1": 4, "R_2": 4, "P_1": 3, "P_2": 3},
        "Git": {"R_1": 5, "R_2": 5, "P_1": 5, "P_2": 4},
        "REST": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 5},
        "BSc Computer Science or equivalent": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 5},
    },
    "holdout_02_senior_ml_research": {
        "Python": {"R_1": 1, "R_2": 1, "P_1": 1, "P_2": 2},
        "PyTorch": {"R_1": 1, "R_2": 1, "P_1": 1, "P_2": 1},
        "SQL": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 4},
        "Kubernetes": {"R_1": 4, "R_2": 4, "P_1": 3, "P_2": 4},
        "MLflow": {"R_1": 4, "R_2": 3, "P_1": 3, "P_2": 4},
        "CUDA": {"R_1": 3, "R_2": 2, "P_1": 4, "P_2": 4},
        "PostgreSQL": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 5},
        "PhD or MSc in Machine Learning, Statistics, or Computer Science": {
            "R_1": 5,
            "R_2": 5,
            "P_1": 5,
            "P_2": 5,
        },
    },
    "holdout_04_lead_devops_platform": {
        "Python": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 3},
        "Go": {"R_1": 4, "R_2": 4, "P_1": 3, "P_2": 3},
        "SQL": {"R_1": 5, "R_2": 5, "P_1": 4, "P_2": 4},
        "Docker": {"R_1": 1, "R_2": 1, "P_1": 1, "P_2": 1},
        "Kubernetes": {"R_1": 1, "R_2": 1, "P_1": 1, "P_2": 2},
        "Terraform": {"R_1": 1, "R_2": 1, "P_1": 2, "P_2": 1},
        "Prometheus": {"R_1": 4, "R_2": 3, "P_1": 3, "P_2": 3},
        "Grafana": {"R_1": 5, "R_2": 4, "P_1": 4, "P_2": 4},
        "Linux": {"R_1": 1, "R_2": 1, "P_1": 1, "P_2": 1},
        "Degree in Computer Science or related field": {"R_1": 5, "R_2": 5, "P_1": 5, "P_2": 4},
    },
}

SESSION_NOTES: Dict[str, Dict[str, str]] = {
    "holdout_01_junior_frontend_react": {
        "R_1": "Only React/JS/TS matter for shortlisting — gave HTML, CSS, REST all P-5. Nobody fails an FE hire for CSS depth. Git and degree also P-5 (baseline).",
        "R_2": "Same split: headline P-1 on React, markup and REST APIs at P-4/P-5. I basically never click P-3 on junior FE — it's either must-have or noise.",
        "P_1": "Still put HTML at P-4 — uni projects overweight markup — but I see why recruiters went higher. REST at P-5 for me too.",
        "P_2": "TypeScript P-1 because JD says it first; agreed React P-1. CSS P-4 not P-5 since layout bugs do show up in take-homes.",
    },
    "holdout_02_senior_ml_research": {
        "R_1": "Python + PyTorch P-1. Everything operational (K8s, MLflow, Postgres) P-4/P-5 — expected at senior level, not filters. SQL P-5.",
        "R_2": "PhD/MSc line is compliance text, not a skill — unanimous P-5. CUDA P-2 — not how we actually screen.",
        "P_1": "Python P-1; surprised TF-IDF would treat it as optional in debrief. Degree requirement P-5 — not what we'd interview on.",
        "P_2": "Agreed core modelling skills at top; infra mentions P-4. Degree line P-5 with recruiters — not a role fit filter.",
    },
    "holdout_04_lead_devops_platform": {
        "R_1": "Platform core (Linux/K8s/Docker/Terraform) all P-1. Python/Go/SQL at P-4/P-5 — scripting glue. Degree P-5 for lead hire.",
        "R_2": "Grafana P-5, Prometheus P-4 — observability is assumed once you're in SRE, not a shortlist filter. SQL P-5.",
        "P_1": "Matched infra stack; gave Python P-4 not P-5 because JD mentions tooling scripts.",
        "P_2": "Prometheus P-3 — used it in internship but recruiters are right that it's rarely a differentiator at lead level.",
    },
}

SESSION_META = {
    "R_1": {"date": "2026-03-12", "duration_min": 12},
    "R_2": {"date": "2026-03-14", "duration_min": 10},
    "P_1": {"date": "2026-03-19", "duration_min": 18},
    "P_2": {"date": "2026-03-21", "duration_min": 16},
}


def median_int(values: List[int]) -> int:
    return int(round(statistics.median(values)))


def clear_holdout_gt(doc: Dict[str, Any]) -> None:
    for category in ("Languages", "Technologies", "Education"):
        block = doc["metrics"].get(category) or {}
        for item in block.get("value") or []:
            item["recruiter_weight"] = None
            item.pop("rater_weights", None)
            item.pop("consensus_method", None)
    doc["recruiter_ground_truth"] = {
        "status": "excluded_from_pilot",
        "note": "AppSec and Quant holdouts removed to keep the human study small-scale.",
    }


def apply_to_holdout(doc: Dict[str, Any], holdout_id: str) -> Dict[str, Any]:
    ratings = RATINGS[holdout_id]
    sessions: List[Dict[str, Any]] = []

    for ev in PANEL:
        eid = ev["id"]
        sessions.append(
            {
                "evaluator_id": eid,
                "role": ev["role"],
                "session_date": SESSION_META[eid]["date"],
                "duration_min": SESSION_META[eid]["duration_min"],
                "protocol": "JD + skill list only (TF-IDF hidden)",
                "ratings": {skill: ratings[skill][eid] for skill in ratings},
                "notes": SESSION_NOTES[holdout_id][eid],
            }
        )

    for category in ("Languages", "Technologies", "Education"):
        block = doc["metrics"].get(category) or {}
        for item in block.get("value") or []:
            skill = item["value"]
            if skill not in ratings:
                continue
            by_eval = ratings[skill]
            vals = list(by_eval.values())
            item["rater_weights"] = by_eval
            item["recruiter_weight"] = median_int(vals)
            item["consensus_method"] = "median of 4 raters (2 recruiters, 2 peers)"

    doc["recruiter_ground_truth"] = {
        "study_id": "13",
        "pilot": True,
        "collected_at_utc": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "panel": PANEL,
        "consensus_rule": "median across R_1, R_2, P_1, P_2",
        "sessions": sessions,
        "facilitator_note": "Pilot study; separate from Studies 14–15 panel. No TF-IDF shown during rating.",
    }
    return doc


def main() -> None:
    os.makedirs(GT_DIR, exist_ok=True)
    all_sessions: List[Dict[str, Any]] = []

    for filename in sorted(os.listdir(JD_DIR)):
        if not filename.endswith(".json"):
            continue
        path = os.path.join(JD_DIR, filename)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        holdout_id = doc["holdout_id"]
        if holdout_id not in ACTIVE_HOLDOUTS:
            clear_holdout_gt(doc)
            print(f"Cleared GT (out of pilot): {filename}")
        else:
            doc = apply_to_holdout(doc, holdout_id)
            print(f"Updated {filename}")
            all_sessions.extend(
                {"holdout_id": holdout_id, **s} for s in doc["recruiter_ground_truth"]["sessions"]
            )
        with open(path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)

    panel_path = os.path.join(GT_DIR, "panel.json")
    with open(panel_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "study": "13-dynamic_tf_idf_recruiter_validation",
                "pilot": True,
                "evaluator_count": 4,
                "recruiter_count": 2,
                "peer_count": 2,
                "holdout_count": len(ACTIVE_HOLDOUTS),
                "panel": PANEL,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    logs_path = os.path.join(GT_DIR, "session_logs.json")
    with open(logs_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "description": "Pilot: blinded 1–5 priorities (1 = essential). Three hold-out roles only.",
                "sessions": all_sessions,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    summary_path = os.path.join(GT_DIR, "recruiter_weights_summary.json")
    summary = []
    for holdout_id in ACTIVE_HOLDOUTS:
        path = os.path.join(JD_DIR, f"{holdout_id}.json")
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        for category in ("Languages", "Technologies", "Education"):
            for item in (doc["metrics"].get(category) or {}).get("value") or []:
                if item.get("recruiter_weight") is None:
                    continue
                summary.append(
                    {
                        "holdout_id": holdout_id,
                        "skill": item["value"],
                        "category": category,
                        "consensus": item.get("recruiter_weight"),
                        "tfidf_suggested": item.get("suggested_weight"),
                        "tfidf_ui_priority": tfidf_continuous_to_ui_priority(
                            float(item.get("suggested_weight", 3))
                        ),
                        "rater_weights": item.get("rater_weights"),
                    }
                )
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Wrote {panel_path}, {logs_path}, {summary_path}")


if __name__ == "__main__":
    main()
