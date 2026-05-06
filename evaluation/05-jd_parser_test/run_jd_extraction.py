import os
import sys
import json
from tqdm import tqdm

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
sys.path.append(project_root)

from backend.core.parsers.job_description import parse_jd

def run_jd_extraction():
    jd_dir = os.path.join(current_dir, "test_data/jds")
    output_dir = os.path.join(current_dir, "output")
    os.makedirs(output_dir, exist_ok=True)

    jd_files = [f for f in os.listdir(jd_dir) if f.endswith(".pdf")]
    
    print(f"Extracting data from {len(jd_files)} Job Descriptions...")
    for filename in tqdm(jd_files):
        path = os.path.join(jd_dir, filename)
        try:
            parsed_data = parse_jd(path)
            
            # Save to JSON
            output_filename = filename.replace(".pdf", ".json")
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(parsed_data, f, indent=4)
        except Exception as e:
            print(f"  [ERROR] Failed to parse {filename}: {e}")

if __name__ == "__main__":
    run_jd_extraction()
