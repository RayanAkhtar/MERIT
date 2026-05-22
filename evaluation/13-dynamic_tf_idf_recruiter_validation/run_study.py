"""
Study 13: Compare recruiter metric priorities (ground truth) vs TF-IDF predictions.

Usage:
    python build_market_corpus.py
    python build_test_dataset.py
    python run_study.py
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from typing import Any, Dict, List, Tuple

from scipy.stats import spearmanr

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, REPO_ROOT)

from corpus_loader import load_corpus_descriptions  # noqa: E402
from priority_scale import tfidf_continuous_to_ui_priority  # noqa: E402
from test_data_loader import load_jds_from_dir  # noqa: E402
from weighting_offline import OfflineWeightingEngine  # noqa: E402

OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")


def _iter_skill_pairs(doc: Dict[str, Any]) -> List[Tuple[str, int | None, float]]:
    pairs: List[Tuple[str, int | None, float]] = []
    metrics = doc.get("metrics") or {}
    for category in ("Languages", "Technologies", "Education"):
        block = metrics.get(category) or {}
        for item in block.get("value") or []:
            skill = item.get("value")
            recruiter = item.get("recruiter_weight")
            suggested = item.get("suggested_weight", 3.0)
            if skill is None:
                continue
            pairs.append((skill, recruiter, float(suggested)))
    return pairs


def score_holdout(doc: Dict[str, Any], engine: OfflineWeightingEngine) -> Dict[str, Any]:
    raw = doc.get("raw_text") or ""
    pairs = _iter_skill_pairs(doc)
    skills = [p[0] for p in pairs]
    weights = engine.calculate_weights(raw, skills)

    recruiter_vals: List[int] = []
    tfidf_vals: List[int] = []
    rows: List[Dict[str, Any]] = []

    for skill, recruiter, _ in pairs:
        if recruiter is None:
            continue
        pred_cont = weights[skill]["weight"]
        pred = tfidf_continuous_to_ui_priority(pred_cont)
        recruiter_vals.append(int(recruiter))
        tfidf_vals.append(pred)
        rows.append(
            {
                "holdout_id": doc.get("holdout_id"),
                "skill": skill,
                "recruiter_weight": int(recruiter),
                "tfidf_continuous": pred_cont,
                "tfidf_likert": pred,
                "exact_match": int(recruiter) == pred,
                "abs_error": abs(int(recruiter) - pred),
            }
        )

    exact = sum(r["exact_match"] for r in rows) / len(rows) if rows else None
    mae = sum(r["abs_error"] for r in rows) / len(rows) if rows else None
    rho, pval = (None, None)
    if len(rows) >= 2:
        rho, pval = spearmanr(recruiter_vals, tfidf_vals)

    return {
        "holdout_id": doc.get("holdout_id"),
        "n_skills": len(rows),
        "exact_match_rate": exact,
        "mae": mae,
        "spearman_rho": float(rho) if rho is not None else None,
        "spearman_p": float(pval) if pval is not None else None,
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd-dir", default=os.path.join(SCRIPT_DIR, "test_data", "job_descriptions"))
    parser.add_argument("--include-pending", action="store_true", help="Score all holdouts, not only those with GT")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    corpus = load_corpus_descriptions()
    engine = OfflineWeightingEngine(corpus)

    jds = load_jds_from_dir(args.jd_dir, require_ground_truth=not args.include_pending)
    if not jds:
        print("[Study 13] No holdouts with recruiter_weight set. Collect GT, or pass --include-pending.")
        print("         See test_data/ground_truth/README.md")
        return

    summaries = []
    all_rows: List[Dict[str, Any]] = []
    for doc in jds:
        result = score_holdout(doc, engine)
        summaries.append({k: v for k, v in result.items() if k != "rows"})
        all_rows.extend(result["rows"])

    with open(os.path.join(OUTPUT_DIR, "per_skill_results.csv"), "w", encoding="utf-8", newline="") as f:
        if all_rows:
            writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
            writer.writeheader()
            writer.writerows(all_rows)

    with open(os.path.join(OUTPUT_DIR, "holdout_summary.csv"), "w", encoding="utf-8", newline="") as f:
        if summaries:
            writer = csv.DictWriter(f, fieldnames=list(summaries[0].keys()))
            writer.writeheader()
            writer.writerows(summaries)

    n = len(all_rows)
    agg = {
        "holdouts_scored": len(summaries),
        "skills_scored": n,
        "exact_match_rate": sum(r["exact_match"] for r in all_rows) / n if n else None,
        "mae": sum(r["abs_error"] for r in all_rows) / n if n else None,
    }
    if n >= 2:
        rec = [r["recruiter_weight"] for r in all_rows]
        pred = [r["tfidf_likert"] for r in all_rows]
        rho, pval = spearmanr(rec, pred)
        agg["spearman_rho"] = float(rho)
        agg["spearman_p"] = float(pval)

    report = {"aggregate": agg, "holdouts": summaries}
    with open(os.path.join(OUTPUT_DIR, "evaluation_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))

    try:
        from generate_charts import generate_all

        charts = generate_all()
        print(f"[Study 13] Generated {len(charts)} charts in output/")
    except Exception as exc:
        print(f"[Study 13] Chart generation skipped: {exc}")


if __name__ == "__main__":
    main()
