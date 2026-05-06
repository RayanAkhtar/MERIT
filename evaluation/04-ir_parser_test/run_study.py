import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

def run_study_04():
    print("--- Phase 1: CV Information Extraction ---")
    from run_extraction import run_extraction
    run_extraction()

    print("\n--- Phase 2: Accuracy Benchmarking ---")
    from run_accuracy_test import run_test
    run_test()

    print("\n--- Phase 3: Visualization Generation ---")
    from generate_ir_visualisations import generate_accuracy_plots
    generate_accuracy_plots()

if __name__ == "__main__":
    run_study_04()
