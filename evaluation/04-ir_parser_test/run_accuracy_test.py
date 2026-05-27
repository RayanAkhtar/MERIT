import os
import json
import pandas as pd
import unicodedata

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "output")
ground_truth_dir = os.path.join(current_dir, "ground_truth")


def output_stem_to_gt_stem(output_stem: str) -> str:
    """Map parsed output basename (no .json) to canonical ground-truth stem.

    Multi-column PDFs are parsed to ``{name}_multi_col.json`` but share the same
    expected labels as ``{name}.json`` — compare both against ``{name}_ground_truth.json``.
    """
    suffix = "_multi_col"
    if output_stem.endswith(suffix):
        return output_stem[: -len(suffix)]
    return output_stem


def normalize_string(s):
    """Normalize unicode strings to ASCII, removing accents and diacritics."""
    if not s:
        return ""
    # Normalize to NFD and filter out non spacing marks
    normalized = unicodedata.normalize('NFD', s)
    return "".join([c for c in normalized if not unicodedata.combining(c)]).lower().strip()

def calculate_metrics(extracted, ground_truth):
    if not ground_truth:
        return None, None
    
    # Skills Comparison (Set-based)
    et_skills_raw = extracted.get("skills", [])
    gt_skills_raw = ground_truth.get("skills", [])
    
    et_skills = set(normalize_string(s) for s in et_skills_raw)
    gt_skills = set(normalize_string(s) for s in gt_skills_raw)
    
    tp_skills = et_skills.intersection(gt_skills)
    fp_skills = et_skills - gt_skills
    fn_skills = gt_skills - et_skills
    
    p_skills = len(tp_skills) / (len(tp_skills) + len(fp_skills)) if (len(tp_skills) + len(fp_skills)) > 0 else 0
    r_skills = len(tp_skills) / (len(tp_skills) + len(fn_skills)) if (len(tp_skills) + len(fn_skills)) > 0 else 0
    f1_skills = 2 * (p_skills * r_skills) / (p_skills + r_skills) if (p_skills + r_skills) > 0 else 0
    
    # Entity Recognition (Experience/Education)
    et_exp = [normalize_string(e.get("name", "")) for e in extracted.get("cv_experience", []) if e.get("name")]
    gt_exp = [normalize_string(e) for e in ground_truth.get("experience", [])]
    
    matched_exp = [gt for gt in gt_exp if any(gt in et for et in et_exp)]
    missed_exp = [gt for gt in gt_exp if gt not in matched_exp]
    
    r_exp = len(matched_exp) / len(gt_exp) if len(gt_exp) > 0 else 0
    
    metrics = {
        "Skill Precision": p_skills,
        "Skill Recall": r_skills,
        "Skill F1": f1_skills,
        "Experience Recall": r_exp,
        "Name Match": 1 if normalize_string(extracted.get("name")) == normalize_string(ground_truth.get("name")) and extracted.get("name") else 0,
        "Email Match": 1 if normalize_string(extracted.get("email")) == normalize_string(ground_truth.get("email")) and extracted.get("email") else 0
    }
    
    diff = {
        "Skills": {
            "Matched": sorted(list(tp_skills)),
            "Missed (False Negatives)": sorted(list(fn_skills)),
            "Extra (False Positives/Noise)": sorted(list(fp_skills))
        },
        "Experience": {
            "Matched": matched_exp,
            "Missed": missed_exp,
            "All Extracted Entities": et_exp
        },
        "Contact Info": {
            "Name Correct": metrics["Name Match"] == 1,
            "Email Correct": metrics["Email Match"] == 1,
            "Extracted": {"name": extracted.get("name"), "email": extracted.get("email")},
            "Expected": {"name": ground_truth.get("name"), "email": ground_truth.get("email")}
        }
    }
    
    return metrics, diff

def run_test():
    results = []
    diff_dir = os.path.join(output_dir, "diff")
    os.makedirs(diff_dir, exist_ok=True)

    manifest_path = os.path.join(current_dir, "test_data", "layout_manifest.csv")
    allowed_output_stems = None
    if os.path.exists(manifest_path):
        manifest_df = pd.read_csv(manifest_path)
        allowed_output_stems = {
            os.path.splitext(os.path.basename(f))[0] for f in manifest_df["File"]
        }

    for output_filename in sorted(os.listdir(output_dir)):
        if not output_filename.endswith(".json"):
            continue
        output_path = os.path.join(output_dir, output_filename)
        if not os.path.isfile(output_path):
            continue

        output_stem = output_filename[:-5]  # strip .json
        if allowed_output_stems is not None and output_stem not in allowed_output_stems:
            continue

        gt_stem = output_stem_to_gt_stem(output_stem)
        gt_filename = f"{gt_stem}_ground_truth.json"
        gt_path = os.path.join(ground_truth_dir, gt_filename)

        if not os.path.exists(gt_path):
            continue

        with open(output_path, "r", encoding="utf-8") as f:
            extracted = json.load(f)

        with open(gt_path, "r", encoding="utf-8") as f:
            gt = json.load(f)

        metrics, diff = calculate_metrics(extracted, gt)
        if not metrics:
            continue

        metrics["File"] = output_stem + ".pdf"
        results.append(metrics)

        diff_path = os.path.join(diff_dir, f"{output_stem}_diff.json")
        with open(diff_path, "w", encoding="utf-8") as f:
            json.dump(diff, f, indent=4)

    df = pd.DataFrame(results)
    summary_path = os.path.join(current_dir, "output/accuracy_summary.csv")
    df.to_csv(summary_path, index=False)

    print("\n--- IR Parser Accuracy Results ---")
    if len(df) == 0:
        print("No matching output/ground-truth pairs found.")
    else:
        print(df.drop(columns=["File"]).mean())
    print(f"\nDetailed report saved to {summary_path}")

if __name__ == "__main__":
    run_test()
