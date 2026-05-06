import os
import json
import random
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHED_DIR = os.path.join(ROOT_DIR, "../backend/cached")

STUDIES = ["02-runtime_study", "03-spacetime_study"]

PERSONAS = [
    "Alex Rivers", "Buzz Ward", "Carl Corp", "Felix Vance", "Fiona Frost", 
    "Ghost Gary", "Jordan Smith", "Kim Junior", "Nadia Nomad", "Sam Old"
]

def load_cached_files(subfolder):
    dir_path = os.path.join(CACHED_DIR, subfolder)
    files = []
    if os.path.exists(dir_path):
        for f in os.listdir(dir_path):
            if f.endswith(".json"):
                with open(os.path.join(dir_path, f), "r", encoding="utf-8") as file:
                    files.append(json.load(file))
    return files

def anonymize_cv(cv_data, name):
    anon = cv_data.copy()
    anon["name"] = name
    anon["email"] = f"{name.lower().replace(' ', '.')}@example.com"
    anon["phone"] = "+440000000000"
    
    anon["links"] = {
        "linkedin": [f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}"],
        "github": [f"https://github.com/{name.lower().replace(' ', '')}"],
        "other": []
    }
    
    if "raw_cv_text" in anon and anon["raw_cv_text"]:
        anon["raw_cv_text"] = f"{name}\n" + anon["raw_cv_text"][100:] 
    
    if "cv_url" in anon:
        anon["cv_url"] = ""
    
    return anon

def anonymize_github(gh_data, name):
    anon = gh_data.copy()
    anon["name"] = name
    anon["username"] = name.lower().replace(' ', '')
    anon["email"] = f"{name.lower().replace(' ', '.')}@example.com"
    anon["avatar_url"] = ""
    anon["profile_url"] = f"https://github.com/{anon['username']}"
    
    if "repositories" in anon:
        for i, repo in enumerate(anon["repositories"]):
            repo["url"] = f"https://github.com/{anon['username']}/repo_{i}"
            repo["name"] = f"Project_{i}"
            repo["description"] = ""
            
    if "featured_projects" in anon:
        for i, proj in enumerate(anon["featured_projects"]):
            proj["url"] = f"https://github.com/{anon['username']}/featured_{i}"
            proj["name"] = f"Featured_{i}"
            proj["description"] = ""
            
    return anon

def anonymize_linkedin(li_data, name):
    anon = li_data.copy()
    anon["full_name"] = name
    anon["first_name"] = name.split()[0]
    anon["last_name"] = name.split()[-1] if len(name.split()) > 1 else ""
    anon["profile_url"] = f"https://www.linkedin.com/in/{name.lower().replace(' ', '-')}"
    anon["avatar_url"] = ""
    anon["public_identifier"] = name.lower().replace(' ', '-')
    
    if "experiences" in anon:
        for exp in anon["experiences"]:
            if "company_url" in exp: exp["company_url"] = ""
            if "company_logo_url" in exp: exp["company_logo_url"] = ""
            if "company_linkedin_url" in exp: exp["company_linkedin_url"] = ""
            
    if "education" in anon:
        for edu in anon["education"]:
            if "school_url" in edu: edu["school_url"] = ""
            if "school_logo_url" in edu: edu["school_logo_url"] = ""
            if "school_linkedin_url" in edu: edu["school_linkedin_url"] = ""
            
    return anon

def main():
    print("Loading cached data...")
    cvs = load_cached_files("cv")
    githubs = load_cached_files("github")
    linkedins = load_cached_files("linkedin")
    
    if not cvs:
        print("No cached CVs found. Exiting.")
        return

    if not githubs: githubs = [{}]
    if not linkedins: linkedins = [{}]

    for study in STUDIES:
        study_path = os.path.join(ROOT_DIR, study, "test_data", "candidates")
        
        for sub in ["cv", "github", "linkedin"]:
            target_dir = os.path.join(study_path, sub)
            os.makedirs(target_dir, exist_ok=True)
            for f in os.listdir(target_dir):
                if f.endswith(".json"):
                    try:
                        os.remove(os.path.join(target_dir, f))
                    except Exception as e:
                        print(f"Skipping deletion of {f}: {e}")
            
        print(f"Generating 25 anonymous candidates for {study}...")
        
        for i, persona in enumerate(PERSONAS):
            file_name = persona.lower().replace(" ", "_") + ".json"
            
            base_cv = cvs[i % len(cvs)]
            base_gh = githubs[i % len(githubs)]
            base_li = linkedins[i % len(linkedins)]
            
            anon_cv = anonymize_cv(base_cv, persona)
            anon_gh = anonymize_github(base_gh, persona) if base_gh else {}
            anon_li = anonymize_linkedin(base_li, persona) if base_li else {}
            
            with open(os.path.join(study_path, "cv", file_name), "w", encoding="utf-8") as f:
                json.dump(anon_cv, f, indent=4)
                
            if anon_gh and persona != "Ghost Gary":
                with open(os.path.join(study_path, "github", file_name), "w", encoding="utf-8") as f:
                    json.dump(anon_gh, f, indent=4)
                    
            if anon_li and persona not in ["Ghost Gary", "Kim Junior"]:
                with open(os.path.join(study_path, "linkedin", file_name), "w", encoding="utf-8") as f:
                    json.dump(anon_li, f, indent=4)
                    
        print(f"Successfully populated {study}/test_data/candidates/")

if __name__ == "__main__":
    main()
