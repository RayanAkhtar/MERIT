import sys
import os
import psutil
import pandas as pd
import gc

# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '..')))

from engines.traditional_ats import TraditionalATS
from engines.modern_ai_ats import SemanticATSModel
from engines.merit_engine import MeritEngine
from common.utils import load_job_description, load_candidates

def get_memory_usage():
    gc.collect() 
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024) 

def benchmark_spacetime():
    jd = load_job_description(current_dir)
    candidate_counts = [10, 50, 100, 200, 500]
    
    print("--- Phase 0: Data Warm-up ---")
    _ = load_candidates(current_dir, limit=1)
    gc.collect()

    print("\n--- Phase 1: Static Engine Load ---")
    load_results = []
    engine_instances = {}
    
    configs = [
        ("Traditional ATS", lambda: TraditionalATS(jd)),
        ("Modern AI ATS", lambda: SemanticATSModel(jd)),
        ("MERIT Explainable", lambda: MeritEngine(jd, explainable=True)),
        ("MERIT Full", lambda: MeritEngine(jd)),
        ("MERIT CV-Only", lambda: MeritEngine(jd, cv_only=True))
    ]

    for name, init_fn in configs:
        print(f"  Measuring {name}...")
        mem_before = get_memory_usage()
        engine = init_fn()
        # Trigger first inference to ensure all weights are in memory
        engine.score_candidate(load_candidates(current_dir, limit=1)[0])
        mem_after = get_memory_usage()
        
        load_cost = mem_after - mem_before
        print(f"    Measured Static Load: {load_cost:.2f} MB")
        load_results.append({"Engine": name, "Static Load (MB)": round(max(0.1, load_cost), 2)})
        engine_instances[name] = engine

    print("\n--- Phase 2: Batch Scaling Complexity ---")
    scaling_results = []
    
    for count in candidate_counts:
        print(f"  Processing batch of {count}...")
        candidates = load_candidates(current_dir, limit=count)
        row = {"Candidates": count}
        
        from tqdm.auto import tqdm
        for name, engine in engine_instances.items():
            # ISOLATED MEASUREMENT: Measure delta only for this specific execution
            gc.collect()
            mem_before_batch = get_memory_usage()
            
            results_in_memory = []
            for c in tqdm(candidates, desc=f"Spacetime: {name}", leave=False):
                if isinstance(engine, MeritEngine):
                    results_in_memory.append(engine.score_candidate(c, include_audit=True))
                else:
                    results_in_memory.append(engine.score_candidate(c))
            
            mem_after_batch = get_memory_usage()
            delta = mem_after_batch - mem_before_batch
            
            # Record the delta (the memory overhead of the results + processing)
            row[f"{name} (MB)"] = round(max(0.01, delta), 2)
            
            del results_in_memory
            gc.collect()
            
        scaling_results.append(row)

    # Save outputs
    os.makedirs(os.path.join(current_dir, "output"), exist_ok=True)
    pd.DataFrame(scaling_results).to_csv(os.path.join(current_dir, "output/spacetime_results.csv"), index=False)
    pd.DataFrame(load_results).to_csv(os.path.join(current_dir, "output/engine_load_costs.csv"), index=False)
    
    print("\n--- Spacetime Study Complete ---")

if __name__ == "__main__":
    benchmark_spacetime()
    
    # Generate Visualisations (only when run as a standalone script)
    try:
        from generate_spacetime_visualisations import generate_spacetime_plots
        generate_spacetime_plots()
    except Exception as e:
        print(f"Warning: Could not generate plots: {e}")
    benchmark_spacetime()
