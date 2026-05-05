import re
import csv
import os
import json
from typing import List, Dict, Any

class TraditionalATS:
    """
    this class replicates the naive baseline for my study
    it simulates a standard old-school applicant tracking system
    mostly relies on keyword matching and basic tenure counting
    
    kept intentionally simple to show how easily these systems 
    can be gamed by candidates like buzz ward
    """
    
    def __init__(self, job_description: Dict[str, Any]):
        self.jd = job_description
        # extract target keywords from jd to match against
        self.keywords = []
        metrics = job_description.get("metrics", {})
        for cat in ["Technologies", "Languages"]:
            if cat in metrics:
                self.keywords.extend([k.lower() for k in metrics[cat].get("value", [])])
        
    def score_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        # traditional ats only sees the cv text without external verification
        cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
        cv_text = cv_text.lower()
        
        # keyword frequency check for classic keyword stuffing targets
        keyword_hits = {}
        total_hits = 0
        for kw in self.keywords:
            count = len(re.findall(rf'\b{re.escape(kw)}\b', cv_text))
            if count > 0:
                keyword_hits[kw] = count
                total_hits += count
        
        # total years of experience using a basic linear sum
        total_years = 0
        exp_list = candidate_data.get("experience", [])
        for exp in exp_list:
            total_years += exp.get("years", 0)
            
        # education check replicating basic filters for degree status
        has_degree = 1.0 if any(d in cv_text for d in ["bsc", "msc", "degree", "university", "computer science"]) else 0.0
        
        # simple weighted sum very common in legacy recruitment software
        score = (total_hits * 0.5) + (total_years * 0.3) + (has_degree * 0.2)
        
        return {
            "Candidate Name": candidate_data.get("name"),
            "Score": round(score, 2),
            "Total Years": total_years,
            "Has Degree": "Yes" if has_degree > 0 else "No",
            "Hits": total_hits
        }

def run_baseline_study():
    # load the jd used for the imperial fyp evaluation
    base_dir = os.path.dirname(__file__)
    jd_path = os.path.join(base_dir, 'test_data/job_description/fullstack_developer.json')
    cv_dir = os.path.join(base_dir, 'test_data/candidates/cv')
    output_path = os.path.join(base_dir, 'output/baseline_rankings.csv')
    
    if not os.path.exists(jd_path):
        print(f"Error: Could not find JD at {jd_path}")
        return

    with open(jd_path, 'r') as f:
        jd = json.load(f)
    
    ats = TraditionalATS(jd)
    results = []
    
    # process the 10 personas
    for filename in os.listdir(cv_dir):
        if filename.endswith(".json"):
            with open(os.path.join(cv_dir, filename), 'r') as f:
                cand = json.load(f)
                
            # synthesise the full text if it's missing for the keyword scanner
            if "full_cv_text" not in cand:
                skills_text = ", ".join(cand.get("skills", []))
                exp_text = " ".join([str(e.get("description", "")) for e in cand.get("experience", [])])
                cand["full_cv_text"] = f"{cand.get('summary', '')} {exp_text} {skills_text}"
                
            results.append(ats.score_candidate(cand))
            
    # sort by the ats score to see who won
    results.sort(key=lambda x: x["Score"], reverse=True)
    
    # output results for the comparative analysis
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        headers = ["Rank", "Candidate Name", "Score", "Total Years", "Has Degree", "Hits"]
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for i, res in enumerate(results):
            res["Rank"] = i + 1
            writer.writerow(res)
        
    print("Traditional ATS Rankings:")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['Candidate Name']} - Score: {res['Score']}")

if __name__ == "__main__":
    run_baseline_study()
