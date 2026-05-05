import subprocess
import os
import sys

def execute_full_evaluation_pipeline():
    """
    master runner for the merit comparative study 
    orchestrates the full evaluation pipeline for my project 
    runs the baseline studies and the visualisation engine
    """
    print("="*60)
    print("MERIT EVALUATION SUITE: Comparative Study Runner")
    print("="*60)
    
    # these scripts represent the four stages of my experimental setup
    study_pipeline = [
        "baseline_ats.py",
        "modern_ai_ats.py",
        "merit_cv_only.py",
        "merit_all_sources.py",
        "generate_visualisations.py"
    ]
    
    # ensuring the working directory is set to the evaluation folder
    study_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(study_dir)
    
    # creating the output directory for study results and charts
    os.makedirs("output", exist_ok=True)
    
    for script in study_pipeline:
        print(f"\n[EXECUTING] {script}...")
        try:
            # using the current python interpreter for environment consistency
            result = subprocess.run([sys.executable, script], capture_output=True, text=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"[FATAL ERROR] Pipeline failed at {script}:")
            print(e.stderr)
            sys.exit(1)
            
    print("\n" + "="*60)
    print("EVALUATION PIPELINE COMPLETE")
    print(f"Study data and visualisations saved to: {os.path.join(study_dir, 'output')}")
    print("="*60)

if __name__ == "__main__":
    execute_full_evaluation_pipeline()
