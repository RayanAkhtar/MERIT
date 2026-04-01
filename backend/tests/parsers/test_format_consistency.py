import os
import pytest
import sys
from collections import defaultdict

# add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from core.parsers.job_description import parse_jd

def get_overlap(list1, list2):
    s1 = set([str(x).lower().strip() for x in list1 if x])
    s2 = set([str(x).lower().strip() for x in list2 if x])
    if not s1 and not s2: return 1.0
    if not s1 or not s2: return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def get_similarity_score(output_1, output_2):
    scores = {}
    text_fields = ["job_title", "company", "location", "employment_type", "experience_level", "salary"]
    for f in text_fields:
        v1 = str(output_1.get(f) or "").lower().strip()
        v2 = str(output_2.get(f) or "").lower().strip()
        if v1 in ["none", "null", ""]:
             scores[f] = 1.0 if v2 in ["none", "null", ""] else 0.0
        else:
             scores[f] = 1.0 if v1 == v2 else 0.0

    list_fields = ["technical_skills", "languages", "experience_required", "education_required", "responsibilities", "requirements"]
    for f in list_fields:
        scores[f] = get_overlap(output_1.get(f, []), output_2.get(f, []))
        
    avg = sum(scores.values()) / len(scores)
    return avg, scores

def get_multi_format_samples():
    samples_dir = os.path.join(os.path.dirname(__file__), "data", "job descriptions")
    groups = defaultdict(list)
    for root, _, files in os.walk(samples_dir):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext in [".txt", ".md", ".pdf", ".docx"] and not name.endswith(("_expected", "_actual")):
                
                # group by full path without extension
                job_id = os.path.join(root, name)
                groups[job_id].append(os.path.join(root, f))
    
    comparisons = []
    for job_id, paths in groups.items():
        if len(paths) >= 2:
            name = os.path.basename(job_id)
            rel_dir = os.path.relpath(os.path.dirname(job_id), samples_dir)
            display_name = f"{rel_dir}/{name}"

            # create pairs for comparison
            for i in range(len(paths)):
                for j in range(i + 1, len(paths)):
                    comparisons.append((paths[i], paths[j], display_name))
    return comparisons

@pytest.mark.parametrize("p1, p2, name", get_multi_format_samples())
def test_format_consistency(p1, p2, name):
    ext1 = os.path.splitext(p1)[1]
    ext2 = os.path.splitext(p2)[1]
    
    res1 = parse_jd(p1)
    res2 = parse_jd(p2)
    
    sim, detailed = get_similarity_score(res1, res2)
    
    # 85% seems reasonable for similarity between job descriptions in different formats
    # differences are likely due to whitespace/layout changes in different formats
    # also, this is for a QOL feature, since the user can always update the output from parsing job descriptions
    assert sim >= 0.85, f"Consistency between {ext1} and {ext2} for {name} is too low: {sim:.2%}. Issues: {[k for k, v in detailed.items() if v < 1.0]}"
