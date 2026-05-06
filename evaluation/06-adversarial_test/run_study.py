import os
import sys

def run_study_06():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("Step 1: Generating Adversarial Data...")
    from generate_adversarial_cvs import generate_adversaries
    generate_adversaries()
    
    print("\nStep 2: Running Benchmarks...")
    from run_adversarial_benchmarks import run_adversarial_benchmark
    run_adversarial_benchmark()
    
    print("\nStep 3: Generating Visualisations...")
    from generate_adversarial_visualisations import visualize_adversarial_results
    visualize_adversarial_results()

if __name__ == "__main__":
    run_study_06()
