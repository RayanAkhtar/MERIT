import subprocess
import os
import sys

def run_study(study_path: str, script_name: str):
    print(f"\n>>> Starting {script_name} in {os.path.basename(study_path)}...")
    try:
        result = subprocess.run(
            [sys.executable, script_name], 
            cwd=study_path,
            capture_output=True, 
            text=True, 
            check=True
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        print(e.stderr)

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    


    study_01 = os.path.join(root_dir, "01-comparative_study")
    run_study(study_01, "run_all_studies.py")
    
    study_02 = os.path.join(root_dir, "02-runtime_study")
    run_study(study_02, "run_runtime.py")
    

    study_03 = os.path.join(root_dir, "03-spacetime_study")
    run_study(study_03, "run_spacetime.py")

    study_04 = os.path.join(root_dir, "04-ir_parser_test")
    run_study(study_04, "run_study.py")

    study_05 = os.path.join(root_dir, "05-jd_parser_test")
    run_study(study_05, "run_study.py")

    study_06 = os.path.join(root_dir, "06-adversarial_test")
    run_study(study_06, "run_study.py")


    # spearman studies (07-10)
    print("\n" + "-"*40)
    print("Preparing Spearman Test Data...")
    subprocess.run([sys.executable, os.path.join(root_dir, "prepare_spearman_data.py")], check=True)
    subprocess.run([sys.executable, os.path.join(root_dir, "sabotage_study_10.py")], check=True)

    spearman_studies = [
        "07-spearman_high_discrimination",
        "08-spearman_seniority_bias_audit",
        "09-spearman_peer_competition",
        "10-spearman_signal_dissonance_failure_case"
    ]

    for study_name in spearman_studies:
        study_path = os.path.join(root_dir, study_name)
        run_study(study_path, "run_study.py")



    print("\n" + "="*60)
    print("ALL EVALUATIONS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
