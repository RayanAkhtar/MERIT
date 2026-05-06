import os
import json
import copy

current_dir = os.path.dirname(os.path.abspath(__file__))
base_cv_path = os.path.join(current_dir, "../../backend/cached/cv/ea68bf8496b89b189e701ce000c0efcc.json")
base_github_path = os.path.join(current_dir, "../../backend/cached/github/cb6c17715a27da1ebd04b6b624b9e941.json")
base_linkedin_path = os.path.join(current_dir, "../../backend/cached/linkedin/c1da1185c4692eba4caacbf6b7e4275b.json")

def anonymize_record(data, name):
    """Deep anonymization of a candidate record."""
    d = copy.deepcopy(data)

    if "name" in d: d["name"] = name
    if "full_name" in d: d["full_name"] = name
    if "username" in d: d["username"] = "CandidateHandle"
    if "email" in d: d["email"] = "candidate@example.com"
    if "profile_url" in d: d["profile_url"] = "https://github.com/CandidateHandle"
    if "avatar_url" in d: d["avatar_url"] = "https://avatars.githubusercontent.com/u/113346804?v=4"
    

    if "bio" in d: d["bio"] = None
    if "location" in d: d["location"] = None
    if "company" in d: d["company"] = None
    
    return d

def generate_adversaries():
    with open(base_cv_path, 'r', encoding='utf-8') as f:
        raw_cv = json.load(f)
    with open(base_github_path, 'r', encoding='utf-8') as f:
        raw_gh = json.load(f)
    with open(base_linkedin_path, 'r', encoding='utf-8') as f:
        raw_li = json.load(f)

    # 1. HONEST
    honest_cv = anonymize_record(raw_cv, "Honest Candidate")
    honest_gh = anonymize_record(raw_gh, "Honest Candidate")
    honest_li = anonymize_record(raw_li, "Honest Candidate")
    if "repositories" in honest_gh: del honest_gh["repositories"]

    # 2. GHOST
    ghost_cv = anonymize_record(raw_cv, "The Ghost")
    hidden_skills = ["rust", "kubernetes", "docker", "aws", "typescript"] * 40
    ghost_cv["raw_cv_text"] += "\n\n" + " ".join(hidden_skills)
    ghost_gh = anonymize_record(raw_gh, "The Ghost")
    ghost_gh["languages"] = [{"label": "HTML", "pct": 100.0}]
    ghost_gh["language_history"] = [{"year": "2026", "HTML": 100}]
    if "repositories" in ghost_gh: del ghost_gh["repositories"]
    ghost_li = anonymize_record(raw_li, "The Ghost")

    # 3. FRAUD
    fraud_cv = anonymize_record(raw_cv, "The Fraud")
    fraud_cv["skills"].extend(["typescript", "python", "react", "postgresql"])
    fraud_gh = anonymize_record(raw_gh, "The Fraud")
    fraud_gh["languages"] = [{"label": "HTML", "pct": 99.8}, {"label": "TypeScript", "pct": 0.1}]
    fraud_gh["language_history"] = [{"year": "2026", "HTML": 10000, "TypeScript": 1}]
    if "repositories" in fraud_gh: del fraud_gh["repositories"]
    fraud_li = anonymize_record(raw_li, "The Fraud")

    # 4. STALE
    stale_cv = anonymize_record(raw_cv, "Stale Candidate")
    for exp in stale_cv.get("cv_experience", []):
        exp["start_date"] = "Jan 2015"
        exp["end_date"] = "Jan 2017"
    stale_gh = anonymize_record(raw_gh, "Stale Candidate")
    stale_gh["updated_at"] = "2017-01-01T00:00:00Z"
    stale_gh["language_history"] = [{"year": "2017", "TypeScript": 10000, "Python": 5000}]
    if "repositories" in stale_gh: del stale_gh["repositories"]
    stale_li = anonymize_record(raw_li, "Stale Candidate")

    # 5. GAMER
    gamer_cv = anonymize_record(raw_cv, "The Time Traveler")
    for exp in gamer_cv.get("cv_experience", []):
        exp["start_date"] = "Jan 2024"
        exp["end_date"] = "Present"
    gamer_gh = anonymize_record(raw_gh, "The Time Traveler")
    gamer_gh["updated_at"] = "2026-01-01T00:00:00Z"
    gamer_gh["language_history"] = [{"year": "2026", "TypeScript": 10000, "Python": 5000}]
    if "repositories" in gamer_gh: del gamer_gh["repositories"]
    gamer_li = anonymize_record(raw_li, "The Time Traveler")

    # 6. SQUATTER
    squatter_cv = anonymize_record(raw_cv, "Squatter Candidate")
    squatter_gh = copy.deepcopy(raw_gh)
    squatter_gh["name"] = "Rayan Akhtar" 
    squatter_li = anonymize_record(raw_li, "Squatter Candidate")

    # 7. SHADOW
    shadow_cv = anonymize_record(raw_cv, "The Shadow")
    shadow_gh = {"source": "github", "name": "The Shadow", "languages": [], "language_history": []}
    shadow_li = {"source": "linkedin", "name": "The Shadow", "experience": []}

    # 8. INFLATER
    inflater_cv = anonymize_record(raw_cv, "The Inflater")
    inflater_gh = anonymize_record(raw_gh, "The Inflater")
    inflater_gh["total_stars"] = 1000
    inflater_gh["repo_count"] = 250
    inflater_gh["languages"] = [{"label": "TypeScript", "pct": 100.0}]
    inflater_gh["language_history"] = [{"year": "2026", "TypeScript": 1000000}]
    if "repositories" in inflater_gh: del inflater_gh["repositories"]
    inflater_li = anonymize_record(raw_li, "The Inflater")

    # 9. SMART SQUATTER (Name Injection Bypass)
    # By including the target's full name as a prefix, the ratio stays above 0.7
    smart_squatter_cv = anonymize_record(raw_cv, "Rayan Akhtar Smith")
    smart_squatter_gh = copy.deepcopy(raw_gh) 
    smart_squatter_gh["name"] = "Rayan Akhtar"
    smart_squatter_li = anonymize_record(raw_li, "Rayan Akhtar Smith")


    out_cv = os.path.join(current_dir, "test_data/cvs")
    out_gh = os.path.join(current_dir, "test_data/github")
    out_li = os.path.join(current_dir, "test_data/linkedin")
    os.makedirs(out_cv, exist_ok=True)
    os.makedirs(out_gh, exist_ok=True)
    os.makedirs(out_li, exist_ok=True)

    # Define key fields to keep for MERIT engine
    CV_KEYS = ["name", "skills", "cv_experience", "projects", "education", "raw_cv_text"]
    GH_KEYS = ["name", "languages", "language_history", "updated_at", "total_stars", "repo_count"]
    LI_KEYS = ["name", "experience"]

    candidates = [
        ("honest", honest_cv, honest_gh, honest_li),
        ("ghost", ghost_cv, ghost_gh, ghost_li),
        ("fraud", fraud_cv, fraud_gh, fraud_li),
        ("stale", stale_cv, stale_gh, stale_li),
        ("gamer", gamer_cv, gamer_gh, gamer_li),
        ("squatter", squatter_cv, squatter_gh, squatter_li),
        ("smart_squatter", smart_squatter_cv, smart_squatter_gh, smart_squatter_li),
        ("shadow", shadow_cv, shadow_gh, shadow_li),
        ("inflater", inflater_cv, inflater_gh, inflater_li)
    ]

    for suffix, cv, gh, li in candidates:
        clean_cv = {k: cv[k] for k in CV_KEYS if k in cv}
        clean_gh = {k: gh[k] for k in GH_KEYS if k in gh}
        clean_li = {k: li[k] for k in LI_KEYS if k in li}

        with open(os.path.join(out_cv, f"{suffix}_cv.json"), 'w') as f: json.dump(clean_cv, f, indent=4)
        with open(os.path.join(out_gh, f"{suffix}_gh.json"), 'w') as f: json.dump(clean_gh, f, indent=4)
        with open(os.path.join(out_li, f"{suffix}_li.json"), 'w') as f: json.dump(clean_li, f, indent=4)

    print(f"Generated {len(candidates)} bare-bones adversarial profiles.")

if __name__ == "__main__":
    generate_adversaries()
