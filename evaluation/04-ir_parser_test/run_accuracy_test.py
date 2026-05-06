import os
import json
import pandas as pd
import unicodedata

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "output")

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
    
    gt_files = [f for f in os.listdir(os.path.join(current_dir, "ground_truth")) if f.endswith("_ground_truth.json")]
    
    for gt_filename in gt_files:
        base_name = gt_filename.replace("_ground_truth.json", "")
        output_file = base_name + ".json"
        output_path = os.path.join(output_dir, output_file)
        gt_path = os.path.join(current_dir, "ground_truth", gt_filename)
        
        if not os.path.exists(output_path):
            continue
            
        with open(output_path, "r", encoding="utf-8") as f:
            extracted = json.load(f)
            
        with open(gt_path, "r", encoding="utf-8") as f:
            gt = json.load(f)
        
        metrics, diff = calculate_metrics(extracted, gt)
        if metrics:
            metrics["File"] = base_name + ".pdf"
            results.append(metrics)
            
            diff_path = os.path.join(diff_dir, f"{base_name}_diff.json")
            with open(diff_path, "w", encoding="utf-8") as f:
                json.dump(diff, f, indent=4)
    
    df = pd.DataFrame(results)
    summary_path = os.path.join(current_dir, "output/accuracy_summary.csv")
    df.to_csv(summary_path, index=False)
    
    print("\n--- IR Parser Accuracy Results ---")
    print(df.drop(columns=["File"]).mean())
    print(f"\nDetailed report saved to {summary_path}")

if __name__ == "__main__":
    run_test()
