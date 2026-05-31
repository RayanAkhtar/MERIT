"""
Run all fifteen MERIT evaluation studies (01--15) in numerical order.

Study 01 runs four comparative engines via run_all_studies.py.
Studies 07--10 use committed CV/GitHub/LinkedIn fixtures under each study's test_data/.
Study 13 expects corpus/ and hold-out JSON; build scripts run if the corpus is missing.
"""
from __future__ import annotations

import os
import subprocess
import sys

# (folder_name, entry_script) — one entry per numbered study in the FYP report.
STUDIES: list[tuple[str, str]] = [
    ("01-comparative_study", "run_all_studies.py"),
    ("02-runtime_study", "run_runtime.py"),
    ("03-spacetime_study", "run_spacetime.py"),
    ("04-ir_parser_test", "run_study.py"),
    ("05-jd_parser_test", "run_study.py"),
    ("06-adversarial_test", "run_study.py"),
    ("07-spearman_high_discrimination", "run_study.py"),
    ("08-spearman_seniority_bias_audit", "run_study.py"),
    ("09-spearman_peer_competition", "run_study.py"),
    ("10-spearman_signal_dissonance_failure_case", "run_study.py"),
    ("11-shapley_verification", "run_study.py"),
    ("12-conflict_resolution", "run_study.py"),
    ("13-dynamic_tf_idf_recruiter_validation", "run_study.py"),
    ("14-hci_trial", "run_study.py"),
    ("15-bias_anonymisation_audit", "run_study.py"),
]

# Studies that stream stdout (long runs — progress is useful).
_STREAM_STUDIES: dict[tuple[str, str], str] = {
    ("03-spacetime_study", "run_spacetime.py"): (
        "Study 03 uses one fresh Python process per engine and per (engine, N) pair "
        "(~35 subprocesses). Expect ~10–15 minutes."
    ),
}

STUDY_13_CORPUS = os.path.join("corpus", "corpus_descriptions.json")
STUDY_13_BUILD = ("build_market_corpus.py", "build_test_dataset.py")


def run_script(study_path: str, script_name: str) -> None:
    study_name = os.path.basename(study_path)
    note = _STREAM_STUDIES.get((study_name, script_name))
    stream = note is not None

    print(f"\n>>> Starting {script_name} in {study_name}...")
    if note:
        print(f"    {note}")

    cmd = [sys.executable, script_name]
    try:
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
        print(f"Error running {script_name} in {study_name}:")
        if stream:
            print(f"Exit code: {e.returncode}")
        elif e.stderr:
            print(e.stderr)
        raise


def _ensure_study_13_assets(study_path: str) -> None:
    corpus_file = os.path.join(study_path, STUDY_13_CORPUS)
    if os.path.isfile(corpus_file):
        return
    print("\n>>> Study 13: corpus missing — running build_market_corpus.py ...")
    for script in STUDY_13_BUILD:
        run_script(study_path, script)


def main() -> None:
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 60)
    print("MERIT evaluation suite — Studies 01--15")
    print("=" * 60)

    for folder, script in STUDIES:
        study_path = os.path.join(root_dir, folder)
        if not os.path.isdir(study_path):
            raise FileNotFoundError(f"Missing study directory: {study_path}")
        if not os.path.isfile(os.path.join(study_path, script)):
            raise FileNotFoundError(f"Missing entry script {script} in {study_path}")

        if folder == "13-dynamic_tf_idf_recruiter_validation":
            _ensure_study_13_assets(study_path)

        run_script(study_path, script)

        if folder == "02-runtime_study":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "runtime"],
                cwd=report_charts,
                check=True,
            )

        if folder == "03-spacetime_study":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "spacetime"],
                cwd=report_charts,
                check=True,
            )
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "scalability"],
                cwd=report_charts,
                check=True,
            )

        if folder == "05-jd_parser_test":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "ingestion"],
                cwd=report_charts,
                check=True,
            )

        if folder == "06-adversarial_test":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "adversarial"],
                cwd=report_charts,
                check=True,
            )

        if folder == "10-spearman_signal_dissonance_failure_case":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "spearman"],
                cwd=report_charts,
                check=True,
            )

        if folder == "11-shapley_verification":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "shapley"],
                cwd=report_charts,
                check=True,
            )

        if folder == "13-dynamic_tf_idf_recruiter_validation":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [
                    sys.executable,
                    "generate_report_charts.py",
                    "--only",
                    "study13_scatter_heatmap",
                ],
                cwd=report_charts,
                check=True,
            )

        if folder == "14-hci_trial":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "hci"],
                cwd=report_charts,
                check=True,
            )

        if folder == "15-bias_anonymisation_audit":
            report_charts = os.path.join(root_dir, "report_charts")
            subprocess.run(
                [sys.executable, "generate_report_charts.py", "--only", "bias"],
                cwd=report_charts,
                check=True,
            )

    print("\n" + "=" * 60)
    print("ALL EVALUATIONS COMPLETE (Studies 01--15)")
    print("=" * 60)


if __name__ == "__main__":
    main()
