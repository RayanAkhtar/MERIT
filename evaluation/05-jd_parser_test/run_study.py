import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

def run_study_05():
    print("--- Phase 1: JD Information Extraction ---")
    from run_jd_extraction import run_jd_extraction
    run_jd_extraction()

    print("\n--- Phase 2: Accuracy Benchmarking ---")
    from run_accuracy_test import run_test
    run_test()

    print("\n--- Phase 3: Visualization Generation ---")
    from generate_jd_visualisations import generate_accuracy_plots
    generate_accuracy_plots()

if __name__ == "__main__":
    run_study_05()
