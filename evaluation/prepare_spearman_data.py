import os
import sys
import json
import random
from tqdm import tqdm

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, '../backend'))
sys.path.append(backend_dir)

from core.parsers.cv import parse_cv
from core.parsers.job_description import parse_jd

def generate_github_data(name, is_fit):
    if is_fit:
        stars = random.randint(300, 1200)
        forks = random.randint(50, 300)
        repos = random.randint(10, 40)
        
        # 2025 data (High Activity)
        langs_2025 = {
            "TypeScript": random.randint(15000, 25000),
            "Java": random.randint(8000, 15000),
            "Python": random.randint(5000, 10000),
            "Shell": random.randint(100, 500),
            "Dockerfile": random.randint(50, 200)
        }
        
        # 2024 data (Moderate Activity)
        langs_2024 = {
            "TypeScript": random.randint(10000, 15000),
            "Java": random.randint(5000, 10000),
            "HTML": random.randint(2000, 5000)
        }
    else:
        stars = random.randint(5, 45)
        forks = random.randint(1, 10)
        repos = random.randint(2, 8)
        
        if "ios" in name.lower():
            langs_2025 = {"Swift": random.randint(2000, 5000), "Objective-C": 500}
            langs_2024 = {"Swift": random.randint(1000, 2000)}
        elif "android" in name.lower():
            langs_2025 = {"Kotlin": random.randint(2000, 5000), "Java": 1000}
            langs_2024 = {"Java": random.randint(1000, 2000)}
        else:
            langs_2025 = {"JavaScript": random.randint(500, 1500), "HTML": 200, "CSS": 100}
            langs_2024 = {"JavaScript": random.randint(200, 800)}

    return {
        "total_stars": stars,
        "total_forks": forks,
        "repo_count": repos,
        "featured_projects": [
            {"name": "production-service-core", "stars": int(stars*0.6), "forks": int(forks*0.5), "languages_distribution": langs_2025, "lines": 50000}
        ],
        "language_history": [
            {"year": "2024", **langs_2024},
            {"year": "2025", **langs_2025},
            {"year": "2026", **{k: 0 for k in langs_2025.keys()}} # Future year with 0 counts
        ]
    }

def generate_linkedin_data(name, is_fit):
    connections = random.randint(500, 2500) if is_fit else random.randint(100, 400)
    return {
        "connections": connections,
        "followers": int(connections * 1.2),
        "linkedin_experience": [
            {"title": "Software Engineer", "company": "Major Tech", "years": 4 if is_fit else 1}
        ]
    }

def prepare_study(study_folder):
    print(f"\nPreparing Data for: {study_folder}")
    study_path = os.path.join(current_dir, study_folder)
    
    pdf_cv_dir = os.path.join(study_path, "test_data/candidates/cv_files")
    jd_pdf = os.path.join(study_path, "test_data/job_description/job_description.pdf")
    
    target_base = os.path.join(study_path, "test_data/candidates")
    
    for d in ["cv", "github", "linkedin"]:
        os.makedirs(os.path.join(target_base, d), exist_ok=True)
    os.makedirs(os.path.join(study_path, "test_data/job_description"), exist_ok=True)

    # JD Processing
    if not os.path.exists(jd_pdf):
        print(f"  [WARNING] JD PDF not found at {jd_pdf}")
    else:
        parsed_jd = parse_jd(jd_pdf)
        jd_json_path = os.path.join(study_path, "test_data/job_description/fullstack_developer.json")
        with open(jd_json_path, 'w') as f:
            json.dump(parsed_jd, f, indent=2)

    # Candidate Processing
    if not os.path.exists(pdf_cv_dir):
        print(f"  [ERROR] CV PDF directory not found at {pdf_cv_dir}")
        return

    resumes = [f for f in os.listdir(pdf_cv_dir) if f.endswith(".pdf")]
    
    for f in tqdm(resumes, desc="Processing Candidates"):
        path = os.path.join(pdf_cv_dir, f)
        parsed_cv = parse_cv(path)
        base_name = f.replace(".pdf", ".json")
        
        with open(os.path.join(target_base, "cv", base_name), 'w') as jf:
            json.dump(parsed_cv, jf, indent=2)
            
        is_fit = any(kw in f for kw in ["Backend", "Software_Engineer", "Full_Stack"])
        
        gh_data = generate_github_data(f, is_fit)
        with open(os.path.join(target_base, "github", base_name), 'w') as jf:
            json.dump(gh_data, jf, indent=2)
            
        li_data = generate_linkedin_data(f, is_fit)
        with open(os.path.join(target_base, "linkedin", base_name), 'w') as jf:
            json.dump(li_data, jf, indent=2)

if __name__ == "__main__":
    prepare_study("07-spearman_high_discrimination")
    prepare_study("08-spearman_seniority_bias_audit")
    prepare_study("09-spearman_peer_competition")
    prepare_study("10-spearman_signal_dissonance_failure_case")
