import os
import json
import sys

# add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from core.parsers.job_description import parse_job

def update_expecteds():
    data_dir = os.path.join(os.path.dirname(__file__), "data", "job descriptions")
    
    for root, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".txt"):
                txt_path = os.path.join(root, f)
                expect_path = txt_path.replace(".txt", "_expected.json")
                
                if os.path.exists(expect_path):
                    print(f"Updating {expect_path}...")
                    with open(txt_path, "r", encoding="utf-8") as tf:
                        text = tf.read()
                    
                    # get relative path for source_file field
                    rel_path = os.path.relpath(txt_path, samples_dir)
                    
                    computed = parse_job(text, rel_path)
                    
                    # strip raw_text from expected to keep it clean
                    if "raw_text" in computed:
                        del computed["raw_text"]
                        
                    with open(expect_path, "w", encoding="utf-8") as ef:
                        json.dump(computed, ef, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    update_expecteds()
