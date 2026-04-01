import os
import sys
import json

# this script tells us how well the parser is doing
# compared to the "golden" expected output we wrote.
# Note that it isnt important to have a high percentage for list fields (explained below).
# This a tool to help catch the main parts of a job description for the configuration to avoid significant repitition
# Having too much data captured for list fields (like in the expected output) may not be ideal as it will
# Detract from the overall score by prioritising candidates that simply keyword match for that field later

# how it works:
# for text fields (like title), it checks if they match exactly
# for list fields (like skills), it checks the % of items that overlap (Jaccard Similarity)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.parsers.job_description import parse_job

def get_overlap(list1, list2):
    # see how much two lists have in common
    s1 = set([x.lower().strip() for x in list1 if x])
    s2 = set([x.lower().strip() for x in list2 if x])
    
    # to prevent zero-division errors later
    if not s1 and not s2: 
        # both empty = perfect match
        return 1.0 
    elif not s1 or not s2: 
        # one empty = no match
        return 0.0 
        
    intersect = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return intersect / union

def get_score(output_1, output_2):
    # compare every field and give a 0-1 score
    scores = {}
    
    # basic text fields
    text_fields = ["job_title", "company", "location", "employment_type", "experience_level", "salary"]
    for f in text_fields:
        v1 = str(output_1.get(f) or "").lower().strip()
        v2 = str(output_2.get(f) or "").lower().strip()

        if v1 == v2:
            scores[f] = 1.0
        else:
            scores[f] = 0.0

    # list fields
    list_fields = ["technical_skills", "languages", "experience_required", "education_required", "responsibilities", "requirements"]
    for f in list_fields:
        scores[f] = get_overlap(output_1.get(f, []), output_2.get(f, []))
        
    return scores

def run():
    samples_dir = os.path.join(os.path.dirname(__file__), "data", "job descriptions")
    
    if not os.path.exists(samples_dir):
        print("no samples found!")
        return

    jd_files = []
    for root, _, files in os.walk(samples_dir):
        for f in files:
            if f.endswith(".txt"):
                jd_files.append(os.path.relpath(os.path.join(root, f), samples_dir))
    
    if not jd_files:
        print("nothing to test.")
        return

    print(f"--- Job Parser Evaluator ({len(jd_files)} samples) ---\n")
    
    results = []
    
    for f_name in jd_files:
        f_path = os.path.join(samples_dir, f_name)
        expect_path = os.path.splitext(f_path)[0] + "_expected.json"
        
        if not os.path.exists(expect_path):
            continue
            
        with open(f_path, "r", encoding="utf-8") as f:
            text = f.read()
        with open(expect_path, "r", encoding="utf-8") as f:
            expected_output = json.load(f)
            
        computed_output = parse_job(text, f_name)
        actual_path = os.path.splitext(f_path)[0] + "_actual.json"
        save_got = computed_output.copy()

        with open(actual_path, "w", encoding="utf-8") as f:
            json.dump(save_got, f, indent=2)
        
        file_scores = get_score(computed_output, expected_output)
        avg = sum(file_scores.values()) / len(file_scores)
        
        results.append(file_scores)
        
        print(f"File: {f_name}")
        print(f"  Score: {avg:.2%}")

        # showing which fields did/didnt match
        issues = []
        matches = []
        for k, v in file_scores.items():
            error_rate = 1.0 - v
            if error_rate > 0:
                issues.append(f"{k}: {error_rate:.0%}")
            else:
                matches.append(k)
        
        if matches:
            print(f"  Matches: {', '.join(matches)}")
        if issues:
            print(f"  Issues: {', '.join(issues)}")

        print("-" * 30)

    if not results:
        print("no expected files to compare with.")
        return

    # summary
    print("\n" + "="*40)
    print("FINISHED SUMMARY")
    print("="*40)
    
    totals = {}
    for r in results:
        for f, s in r.items():
            totals[f] = totals.get(f, 0) + s
            
    for f in sorted(totals.keys()):
        avg = totals[f] / len(results)
        print(f"{f:<20}: {avg:>7.2%}")
        
    total_avg = sum(totals.values()) / (len(results) * len(totals))
    print("-" * 40)
    print(f"{'FINAL TOTAL':<20}: {total_avg:>7.2%}")
    print("="*40)

if __name__ == "__main__":
    run()
