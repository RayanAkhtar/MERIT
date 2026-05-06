import os
import json
import pandas as pd
import unicodedata

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "output")

def normalize_string(s):
    if not s:
        return ""
    normalized = unicodedata.normalize('NFD', s)
    return "".join([c for c in normalized if not unicodedata.combining(c)]).lower().strip()

def calculate_metrics(extracted, ground_truth):
    if not ground_truth:
        return None, None
    
    # Skills Comparison (Combined technical_skills and languages from output)
    et_skills_raw = extracted.get("technical_skills", []) + extracted.get("languages", [])
    gt_skills_raw = ground_truth.get("skills", [])
    
    et_skills = set(normalize_string(s) for s in et_skills_raw)
    gt_skills = set(normalize_string(s) for s in gt_skills_raw)
    
    tp_skills = et_skills.intersection(gt_skills)
    fp_skills = et_skills - gt_skills
    fn_skills = gt_skills - et_skills
    
    p_skills = len(tp_skills) / (len(tp_skills) + len(fp_skills)) if (len(tp_skills) + len(fp_skills)) > 0 else 0
    r_skills = len(tp_skills) / (len(tp_skills) + len(fn_skills)) if (len(tp_skills) + len(fn_skills)) > 0 else 0
    f1_skills = 2 * (p_skills * r_skills) / (p_skills + r_skills) if (p_skills + r_skills) > 0 else 0
    
    metrics = {
        "Skill Precision": p_skills,
        "Skill Recall": r_skills,
        "Skill F1": f1_skills,
        "Title Match": 1 if normalize_string(extracted.get("job_title")) == normalize_string(ground_truth.get("job_title")) and extracted.get("job_title") else 0,
        "Company Match": 1 if normalize_string(ground_truth.get("company")) in normalize_string(extracted.get("company")) and extracted.get("company") else 0
    }
    
    diff = {
        "Skills": {
            "Matched": sorted(list(tp_skills)),
            "Missed (False Negatives)": sorted(list(fn_skills)),
            "Extra (False Positives/Noise)": sorted(list(fp_skills))
        },
        "Details": {
            "Title Match": metrics["Title Match"] == 1,
            "Company Match": metrics["Company Match"] == 1,
            "Extracted": {"title": extracted.get("job_title"), "company": extracted.get("company")},
            "Expected": {"title": ground_truth.get("job_title"), "company": ground_truth.get("company")}
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
    summary_path = os.path.join(current_dir, "output/jd_accuracy_summary.csv")
    df.to_csv(summary_path, index=False)
    
    print("\n--- JD Parser Accuracy Results ---")
    print(df.drop(columns=["File"]).mean())
    print(f"\nDetailed report saved to {summary_path}")

if __name__ == "__main__":
    run_test()
