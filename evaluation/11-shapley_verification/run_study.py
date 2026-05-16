import os
import sys

def run_study_11():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    print("Step 1: Running Shapley Axiom Verification...")
    from run_shapley_verification import run_shapley_verification
    run_shapley_verification()

    print("\nStep 2: Generating Visualisations...")
    from generate_shapley_visualisations import generate_visualisations
    generate_visualisations()

if __name__ == "__main__":
    run_study_11()
