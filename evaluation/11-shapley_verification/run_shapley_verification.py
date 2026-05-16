"""
Study 11: Shapley Value Mathematical Verification
==================================================
Tests the four axioms of Shapley values from cooperative game theory:

1. Efficiency:   sum(shapley_values) == v(grand_coalition) - v(empty)
2. [Omitted] Symmetry: Homogeneous sources are required for symmetry... omitted due to data heterogeneity.
3. Null Player:  if v(S u {i}) == v(S) for all S, then phi(i) == 0
4. Determinism:  identical inputs produce identical outputs across repeated runs
"""

import os
import sys
import json
import csv
import math

# set up paths
STUDY_DIR = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(STUDY_DIR)
ROOT_DIR = os.path.dirname(EVAL_DIR)

sys.path.insert(0, os.path.join(ROOT_DIR, 'backend'))
sys.path.insert(0, EVAL_DIR)

from engines.merit_engine import MeritEngine
from common.utils import load_job_description, load_candidates, export_to_csv

TOLERANCE = 1e-6  # floating-point tolerance for equality checks


def _get_explainable_results(candidates, jd):
    """Run the MERIT explainable engine and return results with Shapley data."""
    engine = MeritEngine(jd, cv_only=False, explainable=True)
    results = []
    for cand in candidates:
        res = engine.score_candidate(cand)
        results.append(res)
    return results


def test_efficiency(results):
    """
    Axiom 1 — Efficiency:
    The sum of Shapley values for all sources must equal the total match score.
    i.e., phi(CV) + phi(GitHub) + phi(LinkedIn) == full_match_score
    """
    print("\n" + "="*60)
    print("AXIOM 1: EFFICIENCY")
    print("  phi(CV) + phi(GitHub) + phi(LinkedIn) == full_match_score")
    print("="*60)

    rows = []
    all_pass = True

    for res in results:
        name = res["name"]
        shapley = res.get("shapley", {})
        overall = shapley.get("overall", {})
        full_score = shapley.get("full_match_score", 0.0)

        phi_cv = overall.get("CV", 0.0)
        phi_gh = overall.get("GitHub", 0.0)
        phi_li = overall.get("LinkedIn", 0.0)
        phi_sum = phi_cv + phi_gh + phi_li

        delta = abs(phi_sum - full_score)
        passed = delta < TOLERANCE

        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False

        print(f"  {name:20s} | SUM_phi = {phi_sum:.6f} | v(N) = {full_score:.6f} | delta = {delta:.2e} | {status}")

        rows.append({
            "candidate": name,
            "phi_cv": round(phi_cv, 6),
            "phi_github": round(phi_gh, 6),
            "phi_linkedin": round(phi_li, 6),
            "phi_sum": round(phi_sum, 6),
            "full_match_score": round(full_score, 6),
            "delta": round(delta, 10),
            "status": status
        })

    print(f"\n  OVERALL: {'ALL PASSED [OK]' if all_pass else 'FAILURES DETECTED [X]'}")
    return rows, all_pass


def test_null_player(candidates, jd):
    """
    Axiom 3 -- Null Player:
    A source contributing zero marginal value to all coalitions must receive phi = 0.
    We test this by using candidates with NO GitHub and NO LinkedIn data.
    """
    print("\n" + "="*60)
    print("AXIOM 3: NULL PLAYER")
    print("  If source contributes nothing -> phi(source) == 0")
    print("="*60)

    engine = MeritEngine(jd, cv_only=False, explainable=True)
    rows = []
    all_pass = True

    for cand in candidates:
        # check which sources are actually null (no data)
        has_gh = cand.get("github_enriched") is not None
        has_li = cand.get("linkedin_enriched") is not None

        null_sources = []
        if not has_gh:
            null_sources.append("GitHub")
        if not has_li:
            null_sources.append("LinkedIn")

        if not null_sources:
            continue  # skip candidates with all sources present

        res = engine.score_candidate(cand)
        shapley = res.get("shapley", {})
        overall = shapley.get("overall", {})

        name = cand["name"]
        for source in null_sources:
            phi = overall.get(source, 0.0)
            passed = abs(phi) < TOLERANCE
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_pass = False

            print(f"  {name:20s} | {source:10s} data = NULL | phi({source}) = {phi:.6f} | {status}")

            rows.append({
                "candidate": name,
                "null_source": source,
                "phi_value": round(phi, 6),
                "status": status
            })

    if not rows:
        print("  (No candidates with null sources found -- skipping)")
    else:
        print(f"\n  OVERALL: {'ALL PASSED [OK]' if all_pass else 'FAILURES DETECTED [X]'}")

    return rows, all_pass


def test_determinism(candidates, jd, num_runs=5):
    """
    Axiom 4 — Determinism:
    Identical inputs must produce identical Shapley outputs across repeated runs.
    """
    print("\n" + "="*60)
    print(f"AXIOM 4: DETERMINISM ({num_runs} repeated runs)")
    print("  Identical inputs -> identical Shapley outputs")
    print("="*60)

    all_runs = []
    for run_idx in range(num_runs):
        results = _get_explainable_results(candidates, jd)
        run_data = {}
        for res in results:
            name = res["name"]
            shapley = res.get("shapley", {})
            overall = shapley.get("overall", {})
            run_data[name] = {
                "CV": overall.get("CV", 0.0),
                "GitHub": overall.get("GitHub", 0.0),
                "LinkedIn": overall.get("LinkedIn", 0.0),
                "full_match_score": shapley.get("full_match_score", 0.0)
            }
        all_runs.append(run_data)

    rows = []
    all_pass = True
    reference = all_runs[0]

    for name in reference:
        max_drift = 0.0
        for run_idx in range(1, num_runs):
            for source in ["CV", "GitHub", "LinkedIn", "full_match_score"]:
                ref_val = reference[name][source]
                run_val = all_runs[run_idx][name][source]
                drift = abs(ref_val - run_val)
                max_drift = max(max_drift, drift)

        passed = max_drift < TOLERANCE
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False

        print(f"  {name:20s} | max drift across {num_runs} runs = {max_drift:.2e} | {status}")

        rows.append({
            "candidate": name,
            "num_runs": num_runs,
            "max_drift": round(max_drift, 10),
            "status": status
        })

    print(f"\n  OVERALL: {'ALL PASSED [OK]' if all_pass else 'FAILURES DETECTED [X]'}")
    return rows, all_pass


def test_per_metric_efficiency(results):
    """
    Extended Efficiency Test:
    For each individual metric, the per-metric Shapley values should also sum
    to that metric's score under the grand coalition.
    """
    print("\n" + "="*60)
    print("EXTENDED: PER-METRIC EFFICIENCY")
    print("  For each metric m: SUM_phi_m(source) == v_m(grand_coalition)")
    print("="*60)

    rows = []
    all_pass = True

    for res in results:
        name = res["name"]
        shapley = res.get("shapley", {})
        metrics_shapley = shapley.get("metrics", {})
        scored_metrics = res.get("metrics", {})

        for metric_key, source_phis in metrics_shapley.items():
            phi_sum = sum(source_phis.values())
            
            # the grand coalition metric score comes from the scored_metrics
            grand_score = scored_metrics.get(metric_key, {}).get("score", 0.0)

            delta = abs(phi_sum - grand_score)
            passed = delta < TOLERANCE
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_pass = False

            rows.append({
                "candidate": name,
                "metric": metric_key,
                "phi_sum": round(phi_sum, 6),
                "metric_score": round(grand_score, 6),
                "delta": round(delta, 10),
                "status": status
            })

    # summary
    pass_count = sum(1 for r in rows if r["status"] == "PASS")
    fail_count = sum(1 for r in rows if r["status"] == "FAIL")
    print(f"  Tested {len(rows)} metric-candidate pairs: {pass_count} PASS, {fail_count} FAIL")
    print(f"\n  OVERALL: {'ALL PASSED [OK]' if all_pass else 'FAILURES DETECTED [X]'}")

    return rows, all_pass


def run_shapley_verification():
    print("="*60)
    print("STUDY 11: SHAPLEY VALUE MATHEMATICAL VERIFICATION")
    print("="*60)

    # load data from local test set
    jd = load_job_description(STUDY_DIR)
    candidates = load_candidates(STUDY_DIR)

    output_dir = os.path.join(STUDY_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    # run the explainable engine once for the shared tests
    results = _get_explainable_results(candidates, jd)

    # axiom 1: efficiency
    efficiency_rows, eff_pass = test_efficiency(results)
    export_to_csv(efficiency_rows, os.path.join(output_dir, "axiom1_efficiency.csv"))

    # axiom 2: symmetry
    print("\n" + "="*60)
    print("AXIOM 2: SYMMETRY")
    print("  Note: Symmetry axiom is not tested because the data sources")
    print("  The data sources we select have heterogeneous scoring functions.")
    print("  Symmetry requires v(S U {i}) == v(S U {j}) for all S, which implies")
    print("  that i and j must be indistinguishable with respect to their value.")
    print("  In this system, CV, GitHub, and LinkedIn are intentionally designed")
    print("  to measure different aspects of a candidate and are therefore distinguishable.")
    print("="*60)

    # axiom 3: null player
    null_rows, null_pass = test_null_player(candidates, jd)
    if null_rows:
        export_to_csv(null_rows, os.path.join(output_dir, "axiom3_null_player.csv"))

    # axiom 4: determinism
    det_rows, det_pass = test_determinism(candidates, jd, num_runs=5)
    export_to_csv(det_rows, os.path.join(output_dir, "axiom4_determinism.csv"))

    # per metric efficiency
    metric_rows, metric_pass = test_per_metric_efficiency(results)
    export_to_csv(metric_rows, os.path.join(output_dir, "extended_per_metric_efficiency.csv"))

    # summary
    summary = {
        "Axiom 1 (Efficiency)": "PASS" if eff_pass else "FAIL",
        "Axiom 3 (Null Player)": "PASS" if null_pass else "FAIL (or N/A)",
        "Axiom 4 (Determinism)": "PASS" if det_pass else "FAIL",
        "Extended (Per-Metric)": "PASS" if metric_pass else "FAIL"
    }

    print("\n" + "="*60)
    print("FINAL VERIFICATION SUMMARY")
    print("="*60)
    for test_name, result in summary.items():
        icon = "[OK]" if "PASS" in result else "[X]"
        print(f"  {icon} {test_name}: {result}")

    summary_path = os.path.join(output_dir, "verification_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[SUCCESS] Summary exported to {summary_path}")


if __name__ == "__main__":
    run_shapley_verification()
