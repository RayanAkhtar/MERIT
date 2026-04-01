import os
import json
import pytest
import sys

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from core.parsers.job_description import parse_job

def get_overlap(list1, list2):
    s1 = set([str(x).lower().strip() for x in list1 if x])
    s2 = set([str(x).lower().strip() for x in list2 if x])
    if not s1 and not s2: return 1.0
    if not s1 or not s2: return 0.0
    return len(s1.intersection(s2)) / len(s1.union(s2))

def get_score(computed, expected):
    scores = {}
    text_fields = ["job_title", "company", "location", "employment_type", "experience_level", "salary"]
    for f in text_fields:
        v1 = str(computed.get(f) or "").lower().strip()
        v2 = str(expected.get(f) or "").lower().strip()

        if v2 in ["none", "null", ""]:
             scores[f] = 1.0 if v1 in ["none", "null", ""] else 0.0
        else:
             scores[f] = 1.0 if v1 == v2 else 0.0

    list_fields = ["technical_skills", "languages", "experience_required", "education_required", "responsibilities", "requirements"]
    for f in list_fields:
        scores[f] = get_overlap(computed.get(f, []), expected.get(f, []))
    
    return scores

def get_samples():
    samples_dir = os.path.join(os.path.dirname(__file__), "data", "job descriptions")
    jd_files = []
    for root, _, files in os.walk(samples_dir):
        for f in files:
            if f.endswith(".txt") and not (f.endswith("_expected.json") or f.endswith("_actual.json")):
                txt_path = os.path.join(root, f)
                expect_path = os.path.splitext(txt_path)[0] + "_expected.json"
                if os.path.exists(expect_path):
                    rel_path = os.path.relpath(txt_path, samples_dir)
                    jd_files.append((txt_path, expect_path, rel_path))
    return jd_files

@pytest.mark.parametrize("txt_path, expect_path, rel_path", get_samples())
def test_parser_accuracy(txt_path, expect_path, rel_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read()
    with open(expect_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    computed = parse_job(text, rel_path)
    
    scores = get_score(computed, expected)
    avg_score = sum(scores.values()) / len(scores)
    
    # 50% is a reasonable baseline to ensure we capture a good chunk of information for the user
    # Note that this is mainly a QOL feature, so evaluation isnt too necessary here
    assert avg_score >= 0.50, f"Accuracy for {rel_path} is too low: {avg_score:.2%}. Issues: {[k for k, v in scores.items() if v < 1.0]}"
