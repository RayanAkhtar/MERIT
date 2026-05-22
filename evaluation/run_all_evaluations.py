import subprocess
import os
import sys

# Studies that stream stdout (long runs / many subprocesses — progress is useful).
_STREAM_STUDIES = {
    ("03-spacetime_study", "run_spacetime.py"): (
        "Study 03 uses one fresh Python process per engine and per (engine, N) pair "
        "(~35 subprocesses). Expect ~10–15 minutes."
    ),
}


def run_study(study_path: str, script_name: str):
    study_name = os.path.basename(study_path)
    note = _STREAM_STUDIES.get((study_name, script_name))
    stream = note is not None

    print(f"\n>>> Starting {script_name} in {study_name}...")
    if note:
        print(f"    {note}")

    try:
        cmd = [sys.executable, script_name]
        if stream:
            subprocess.run(cmd, cwd=study_path, check=True)
        else:
            result = subprocess.run(
                cmd,
                cwd=study_path,
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout:
                print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}:")
        if stream:
            print(f"Exit code: {e.returncode}")
        elif e.stderr:
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

    # study 11: shapley verification
    study_11 = os.path.join(root_dir, "11-shapley_verification")
    run_study(study_11, "run_study.py")

    # study 12: conflict resolution
    study_12 = os.path.join(root_dir, "12-conflict_resolution")
    run_study(study_12, "run_study.py")

    # studies 14–15: HCI trial and bias / anonymisation audit
    print("\n" + "-" * 40)
    print("HCI & fairness audits (Studies 14–15)...")
    study_14 = os.path.join(root_dir, "14-hci_trial")
    run_study(study_14, "run_study.py")

    study_15 = os.path.join(root_dir, "15-bias_anonymisation_audit")
    run_study(study_15, "run_study.py")

    study_13 = os.path.join(root_dir, "13-dynamic_tf_idf_recruiter_validation")
    run_study(study_13, "run_study.py")

    print("\n" + "="*60)
    print("ALL EVALUATIONS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
