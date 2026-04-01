import os
import sys
import json
from collections import defaultdict

# This script checks if the parser produces consistent results across different file formats (.txt, .md, .pdf, .docx)
# for the same job description.

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.parsers.job_description import parse_jd

def get_overlap(list1, list2):
    s1 = set([str(x).lower().strip() for x in list1 if x])
    s2 = set([str(x).lower().strip() for x in list2 if x])
    
    if not s1 and not s2: 
        return 1.0 
    elif not s1 or not s2: 
        return 0.0 
        
    intersect = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return intersect / union

def get_similarity_score(output_1, output_2):
    scores = {}
    
    # text fields
    text_fields = ["job_title", "company", "location", "employment_type", "experience_level", "salary"]
    for f in text_fields:
        v1 = str(output_1.get(f) or "").lower().strip()
        v2 = str(output_2.get(f) or "").lower().strip()
        scores[f] = 1.0 if v1 == v2 else 0.0

    # list fields
    list_fields = ["technical_skills", "languages", "experience_required", "education_required", "responsibilities", "requirements"]
    for f in list_fields:
        scores[f] = get_overlap(output_1.get(f, []), output_2.get(f, []))
        
    avg = sum(scores.values()) / len(scores)
    return avg, scores

def run():
    samples_dir = os.path.join(os.path.dirname(__file__), "data", "job descriptions")
    
    if not os.path.exists(samples_dir):
        print("No samples found!")
        return

    # group files by their base name
    groups = defaultdict(list)
    for root, _, files in os.walk(samples_dir):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext in [".txt", ".md", ".pdf", ".docx"] and not name.endswith(("_expected", "_actual")):
                full_path = os.path.join(root, f)
                groups[name].append(full_path)

    print(f"--- Format Consistency Checker ---")
    
    total_similarities = []
    
    for base_name, paths in groups.items():
        if len(paths) < 2:
            continue
            
        print(f"\nChecking Consistency for: {base_name}")
        results = {}
        for p in paths:
            ext = os.path.splitext(p)[1]
            try:
                results[ext] = parse_jd(p)
            except Exception as e:
                print(f"  Error parsing {ext}: {e}")

        # compare every pair
        exts = list(results.keys())
        for i in range(len(exts)):
            for j in range(i + 1, len(exts)):
                ext1, ext2 = exts[i], exts[j]
                sim, detailed = get_similarity_score(results[ext1], results[ext2])
                total_similarities.append(sim)
                print(f"  {ext1} vs {ext2}: {sim:.2%}")
                
                # report differences if not perfect
                if sim < 1.0:
                    diffs = [f"{k} ({v:.0%})" for k, v in detailed.items() if v < 1.0]
                    print(f"    Differences: {', '.join(diffs)}")

    if not total_similarities:
        print("No multi-format samples found to compare.")
    else:
        avg_total = sum(total_similarities) / len(total_similarities)
        print(f"\n{'='*40}")
        print(f"OVERALL CONSISTENCY SCORE: {avg_total:.2%}")
        print(f"{'='*40}")

if __name__ == "__main__":
    run()
