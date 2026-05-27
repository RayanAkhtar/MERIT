import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../../backend')))

from core.parsers.cv import parse_cv

resumes_dir = os.path.join(current_dir, "test_data/resumes")
single_dir = os.path.join(current_dir, "test_data/single-column")
multi_dir = os.path.join(current_dir, "test_data/multi-column")
output_dir = os.path.join(current_dir, "output")
os.makedirs(output_dir, exist_ok=True)

def run_extraction():
    search_dirs = [single_dir, multi_dir, resumes_dir]
    pdf_paths = []
    for d in search_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.lower().endswith(".pdf"):
                pdf_paths.append(os.path.join(d, f))

    # De-duplicate by filename (prefer single/multi over legacy resumes/)
    by_name = {}
    for p in pdf_paths:
        name = os.path.basename(p)
        if name not in by_name:
            by_name[name] = p
    paths = [by_name[k] for k in sorted(by_name.keys())]

    print(f"Extracting data from {len(paths)} resumes...")
    
    for path in paths:
        filename = os.path.basename(path)
        try:
            parsed_data = parse_cv(path)
            report_data = parsed_data.copy()
            
            output_name = filename.replace(".pdf", ".json")
            with open(os.path.join(output_dir, output_name), "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4)
            print(f"  [SUCCESS] {filename}")
        except Exception as e:
            print(f"  [ERROR] {filename}: {e}")

if __name__ == "__main__":
    run_extraction()
