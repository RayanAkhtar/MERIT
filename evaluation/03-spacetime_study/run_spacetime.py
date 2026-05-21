"""
Study 03: Spacetime / memory benchmark.

Each engine and each batch size is measured in a fresh subprocess so RSS reflects
only that engine in memory (no cross-engine contamination in one Python process).
"""
import sys
import os
import gc
import psutil
import pandas as pd
from multiprocessing import get_context

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, "..")))

CANDIDATE_COUNTS = [10, 50, 100, 200, 500]

ENGINE_ORDER = [
    ("traditional", "Traditional ATS"),
    ("modern_ai", "Modern AI ATS"),
    ("merit_cv_only", "MERIT CV-Only"),
    ("merit_full", "MERIT Full"),
    ("merit_explainable", "MERIT Explainable"),
]


def get_memory_usage():
    gc.collect()
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def _create_engine(engine_key, jd):
    """Lazy-import only the engine under test so static RSS is not inflated by other models."""
    if engine_key == "traditional":
        from engines.traditional_ats import TraditionalATS

        return TraditionalATS(jd)
    if engine_key == "modern_ai":
        from engines.modern_ai_ats import SemanticATSModel

        return SemanticATSModel(jd)
    if engine_key == "merit_explainable":
        from engines.merit_engine import MeritEngine

        return MeritEngine(jd, explainable=True)
    if engine_key == "merit_full":
        from engines.merit_engine import MeritEngine

        return MeritEngine(jd)
    if engine_key == "merit_cv_only":
        from engines.merit_engine import MeritEngine

        return MeritEngine(jd, cv_only=True)
    raise ValueError(f"Unknown engine key: {engine_key}")


def _worker_static(engine_key, study_dir, out_queue):
    """Fresh process: measure RSS delta for engine init + one warmup score."""
    sys.path.insert(0, os.path.abspath(os.path.join(study_dir, "..")))
    from common.utils import load_job_description, load_candidates

    jd = load_job_description(study_dir)
    gc.collect()
    mem_before = get_memory_usage()
    engine = _create_engine(engine_key, jd)
    engine.score_candidate(load_candidates(study_dir, limit=1)[0])
    mem_after = get_memory_usage()
    out_queue.put(round(max(0.1, mem_after - mem_before), 2))


def _worker_batch(engine_key, study_dir, count, out_queue):
    """Fresh process: load engine, score N candidates, retain results, report RSS delta."""
    sys.path.insert(0, os.path.abspath(os.path.join(study_dir, "..")))
    from common.utils import load_job_description, load_candidates

    jd = load_job_description(study_dir)
    engine = _create_engine(engine_key, jd)
    candidates = load_candidates(study_dir, limit=count)
    merit_engine = engine_key.startswith("merit")

    gc.collect()
    mem_before = get_memory_usage()

    results_in_memory = []
    for c in candidates:
        if merit_engine:
            results_in_memory.append(engine.score_candidate(c, include_audit=True))
        else:
            results_in_memory.append(engine.score_candidate(c))

    mem_after = get_memory_usage()
    out_queue.put(round(max(0.01, mem_after - mem_before), 2))


def _run_isolated(target, args):
    ctx = get_context("spawn")
    queue = ctx.Queue()
    proc = ctx.Process(target=target, args=(*args, queue))
    proc.start()
    proc.join()
    if proc.exitcode != 0:
        raise RuntimeError(f"Subprocess failed: {target.__name__} exit code {proc.exitcode}")
    return queue.get()


def benchmark_spacetime():
    print("Study 03: isolated subprocess memory benchmark (one process per measurement)")
    print("--- Phase 0: Data warm-up ---")
    from common.utils import load_candidates

    _ = load_candidates(current_dir, limit=1)
    gc.collect()

    print("\n--- Phase 1: Static engine load (one fresh process per engine) ---")
    load_results = []
    for engine_key, display_name in ENGINE_ORDER:
        print(f"  {display_name}...")
        load_mb = _run_isolated(_worker_static, (engine_key, current_dir))
        print(f"    Static load: {load_mb:.2f} MB")
        load_results.append({"Engine": display_name, "Static Load (MB)": load_mb})

    print("\n--- Phase 2: Batch scaling (one fresh process per engine × N) ---")
    scaling_results = []
    for count in CANDIDATE_COUNTS:
        print(f"  N = {count}...")
        row = {"Candidates": count}
        for engine_key, display_name in ENGINE_ORDER:
            print(f"    {display_name}...")
            delta_mb = _run_isolated(_worker_batch, (engine_key, current_dir, count))
            print(f"      Incremental batch RSS: {delta_mb:.2f} MB")
            row[f"{display_name} (MB)"] = delta_mb
        scaling_results.append(row)

    out_dir = os.path.join(current_dir, "output")
    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(scaling_results).to_csv(os.path.join(out_dir, "spacetime_results.csv"), index=False)
    pd.DataFrame(load_results).to_csv(os.path.join(out_dir, "engine_load_costs.csv"), index=False)
    print("\n--- Spacetime study complete ---")


def generate_plots():
    from generate_spacetime_visualisations import generate_spacetime_plots

    generate_spacetime_plots()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Study 03 memory benchmark (isolated subprocess per measurement)."
    )
    parser.add_argument(
        "--plots-only",
        action="store_true",
        help="Regenerate figures from existing CSVs without re-running benchmarks.",
    )
    args = parser.parse_args()

    if not args.plots_only:
        benchmark_spacetime()
    try:
        generate_plots()
    except Exception as e:
        print(f"Warning: Could not generate plots: {e}")
