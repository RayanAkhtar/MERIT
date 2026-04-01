import os
import sys
import json
import difflib

# Due to the nature of job descriptions being inconsistent, we instead
# test for general use cases and aim for a high level of similarity between
# the parsed output and the expected output. The purpose of this file is to
# check for every difference between the parsed output and the expected output
# to flag any significant erroneous behaviour.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from core.parsers.job_description import parse_job


# recursively cleaning the json so we don't get fake diffs due to
# different casing/ordering of elements in the json
def clean_json(obj):
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        try:
            return sorted([clean_json(i) for i in obj])
        except:
            return sorted([clean_json(i) for i in obj], key=lambda x: json.dumps(x, sort_keys=True))
    elif isinstance(obj, str):
        return obj.lower().strip()
    else:
        return obj

def run():
    samples = os.path.join(os.path.dirname(__file__), "data/job descriptions")
    
    if not os.path.exists(samples):
        print("no samples folder!")
        return

    # find all the text files
    files_to_test = []
    for root, _, files in os.walk(samples):
        for f in files:
            if f.endswith(".txt"):
                files_to_test.append(os.path.relpath(os.path.join(root, f), samples))
    
    print(f"--- Checking Diffs ({len(files_to_test)} samples) ---\n")
    
    for f_name in files_to_test:
        f_path = os.path.join(samples, f_name)
        expect_path = os.path.splitext(f_path)[0] + "_expected.json"
        
        print(f"Testing: {f_name}")
        
        with open(f_path, "r", encoding="utf-8") as f:
            text = f.read()
            
        # run the actual parser
        computed_output = parse_job(text, f_name)

        if "raw_text" in computed_output:
            # ignoring the raw_text field, since it is irrelevant for this comparison
            del computed_output["raw_text"]

        # save the actual result for manual checking
        actual_path = os.path.splitext(f_path)[0] + "_actual.json"
        with open(actual_path, "w", encoding="utf-8") as f:
            json.dump(computed_output, f, indent=2)
            
        if not os.path.exists(expect_path):
            print(f"  [ERROR] no expected JSON for {f_name}")
            continue
            
        with open(expect_path, "r", encoding="utf-8") as f:
            expected_results = json.load(f)
            
        computed_results = clean_json(computed_output)
        expected_results = clean_json(expected_results)
            
        if computed_results == expected_results:
            print(f"  [OK] {f_name}")
        else:
            print(f"  [DIFF] {f_name} has changes:")
            # show the differences
            computed_str = json.dumps(computed_results, indent=2, sort_keys=True).splitlines()
            expected_str = json.dumps(expected_results, indent=2, sort_keys=True).splitlines()
            diff = difflib.unified_diff(expected_str, computed_str, fromfile="Expected", tofile="Computed")
            for line in diff:
                print(f"    {line}")
                
    print("\n--- Done ---")

if __name__ == "__main__":
    run()
