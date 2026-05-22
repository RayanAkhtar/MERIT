"""
Build held-out Study 13 job descriptions (not in the 100-doc market corpus).

Writes test_data/job_descriptions/*.json with parsed skills, TF-IDF suggestions,
and recruiter_weight=null until human sessions.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

from corpus_loader import load_corpus_descriptions  # noqa: E402
from weighting_offline import OfflineWeightingEngine  # noqa: E402

OUTPUT_DIR = os.path.join(SCRIPT_DIR, "test_data", "job_descriptions")

# Synthetic holdout JDs — excluded from corpus/ so IDF is not leaked.
HOLDOUTS: List[Dict[str, Any]] = [
    {
        "holdout_id": "holdout_01_junior_frontend_react",
        "job_title": "Junior Frontend Engineer (React)",
        "company": "Lumen UI Labs",
        "experience_level": "Junior",
        "raw_text": """
Lumen UI Labs — Junior Frontend Engineer (React)

Requirements:
- Strong JavaScript and TypeScript skills; daily React development.
- HTML, CSS, and responsive layout experience.
- React hooks, component testing with Jest, and familiarity with REST APIs.
- Git workflow and code review participation.
- Nice to have: Next.js exposure and Figma handoff experience.

Education: BSc Computer Science or equivalent.
""",
        "languages": ["JavaScript", "TypeScript", "HTML", "CSS"],
        "technologies": ["React", "Jest", "Git", "REST"],
        "education": ["BSc Computer Science or equivalent"],
    },
    {
        "holdout_id": "holdout_02_senior_ml_research",
        "job_title": "Senior Machine Learning Engineer",
        "company": "Helix Inference Ltd",
        "experience_level": "Senior",
        "raw_text": """
Helix Inference Ltd — Senior Machine Learning Engineer

You will train and deploy deep learning models in production.
Required: Python, PyTorch, CUDA optimisation, distributed training, MLOps on Kubernetes.
Strong statistics, experiment tracking (MLflow), and transformer architectures.
Research publications or open-source ML contributions are valued.
PostgreSQL and feature-store experience preferred.
PhD or MSc in Machine Learning, Statistics, or Computer Science.
""",
        "languages": ["Python", "SQL"],
        "technologies": ["PyTorch", "Kubernetes", "MLflow", "CUDA", "PostgreSQL"],
        "education": ["PhD or MSc in Machine Learning, Statistics, or Computer Science"],
    },
    {
        "holdout_id": "holdout_04_lead_devops_platform",
        "job_title": "Lead DevOps / Platform Engineer",
        "company": "Streamforge Platforms",
        "experience_level": "Lead",
        "raw_text": """
Streamforge Platforms — Lead DevOps Engineer

Own platform reliability, observability, and delivery pipelines.
Core stack: Linux, Docker, Kubernetes, Terraform, Helm, Prometheus, Grafana, GitHub Actions.
Python and Go for tooling; PostgreSQL for internal services.
On-call leadership and SLO design required.
""",
        "languages": ["Python", "Go", "SQL"],
        "technologies": ["Docker", "Kubernetes", "Terraform", "Prometheus", "Grafana", "Linux"],
        "education": ["Degree in Computer Science or related field"],
    },
]


def _metric_block(category: str, skills: List[str], weights: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    value = []
    for skill in skills:
        w = weights.get(skill, {})
        value.append(
            {
                "value": skill,
                "suggested_weight": w.get("weight", 3.0),
                "suggested_weight_reasoning": w.get("reasoning", ""),
                "suggested_weight_math": w.get("math"),
                "recruiter_weight": None,
            }
        )
    return {"category": category, "value": value}


def build_holdout_doc(spec: Dict[str, Any], engine: OfflineWeightingEngine) -> Dict[str, Any]:
    skills = spec["languages"] + spec["technologies"] + spec["education"]
    weights = engine.calculate_weights(spec["raw_text"].strip(), skills)

    metrics = {
        "Languages": _metric_block("Languages", spec["languages"], weights),
        "Technologies": _metric_block("Technologies", spec["technologies"], weights),
        "Education": _metric_block("Education", spec["education"], weights),
        "Experience": {"category": "Experience", "value": []},
    }

    return {
        "holdout_id": spec["holdout_id"],
        "job_title": spec["job_title"],
        "company": spec["company"],
        "experience_level": spec["experience_level"],
        "raw_text": spec["raw_text"].strip(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": metrics,
        "tfidf_suggested_weights": weights,
        "recruiter_ground_truth": {
            "skill_ratings": {},
            "notes": "Fill recruiter_weight per skill after sessions.",
        },
    }


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    corpus = load_corpus_descriptions()
    engine = OfflineWeightingEngine(corpus)

    for spec in HOLDOUTS:
        doc = build_holdout_doc(spec, engine)
        out_path = os.path.join(OUTPUT_DIR, f"{spec['holdout_id']}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
        print(f"Wrote {out_path}")

    manifest = {
        "holdout_count": len(HOLDOUTS),
        "corpus_documents": len(corpus),
        "note": "Holdouts are not in data/job descriptions/ corpus.",
    }
    with open(os.path.join(SCRIPT_DIR, "test_data", "test_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


if __name__ == "__main__":
    main()
