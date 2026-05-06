import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(current_dir, '../../backend')))

from core.parsers.cv import parse_cv

resumes_dir = os.path.join(current_dir, "test_data/resumes")
output_dir = os.path.join(current_dir, "output")
os.makedirs(output_dir, exist_ok=True)

def run_extraction():
    files = [f for f in os.listdir(resumes_dir) if f.endswith(".pdf")]
    print(f"Extracting data from {len(files)} resumes...")
    
    for filename in files:
        path = os.path.join(resumes_dir, filename)
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
