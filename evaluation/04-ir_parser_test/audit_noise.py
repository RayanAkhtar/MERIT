import os
import json
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
diff_dir = os.path.join(current_dir, "output/diff")
output_dir = os.path.join(current_dir, "output")

def audit_noise():
    diff_files = [f for f in os.listdir(diff_dir) if f.endswith("_diff.json")]
    
    for diff_name in diff_files:
        base_name = diff_name.replace("_diff.json", "")
        with open(os.path.join(diff_dir, diff_name), "r", encoding="utf-8") as f:
            diff = json.load(f)
        
        with open(os.path.join(output_dir, base_name + ".json"), "r", encoding="utf-8") as f:
            output = json.load(f)
            
        noise = diff["Skills"].get("Extra (False Positives/Noise)", [])
        if not noise:
            continue
            
        print(f"\n--- {base_name} ---")
        raw_text = output.get("raw_cv_text", "").lower()
        
        for n in noise:
            # Find context in raw text
            pattern = re.compile(rf".{{0,30}}{re.escape(n.lower())}.{{0,30}}", re.DOTALL)
            match = pattern.search(raw_text)
            if match:
                context = match.group(0).replace("\n", " ")
                print(f"  [NOISE] {n}: ...{context}...")
            else:
                print(f"  [NOISE] {n}: (Not found in raw text?)")

if __name__ == "__main__":
    audit_noise()
