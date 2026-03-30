import os
import re
import csv
from typing import List, Dict, Optional, Union
from docx import Document
from pdfminer.high_level import extract_text

# ============================================================
# Current structure of `job_description`
# ============================================================
#
# {
#     "raw_text": str,                        # full text for debugging and displaying
#     "job_title": str | None,
#     "company": str | None,
#     "location": str | None,
#     "employment_type": str | None,          # Full-time, Internship, Contract
#     "experience_level": str | None,         # Entry, Junior, Mid, Senior
#     "technical_skills": [str],
#     "soft_skills": [str],
#     "responsibilities": [str],
#     "requirements": [str],
#     "education": [str],
#     "nice_to_have": [str],
#     "salary": str | None,
#     "source_file": str
# }
#
# ============================================================


# ----------------------------
# Section Headers
# ----------------------------

SECTION_HEADERS = {
    "responsibilities": ["responsibilities", "role", "what you will do", "duties", "role overview"],
    "requirements": ["requirements", "qualifications", "what we are looking for", "skills", "competencies", "what you will have"],
    "technical_skills": ["technical skills", "stack", "tech stack", "technologies"],
    "education": ["education", "degree", "academic", "university"],
    "nice_to_have": ["nice to have", "preferred", "bonus", "desirable"]
}

# ----------------------------
# File Text Extraction
# ----------------------------

def extract_text_from_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text_from_pdf(path: str) -> str:
    return extract_text(path)


# ----------------------------
# Parsing Helpers
# ----------------------------

def extract_section(text: str, keywords: List[str]) -> List[str]:
    lines = text.splitlines()
    capture = False
    collected = []

    for line in lines:
        lower = line.lower().strip()

        if any(k in lower for k in keywords):
            capture = True
            continue

        if capture:
            if lower == "" or re.match(r"^[A-Z][A-Za-z ]{3,}$", line):
                break
            collected.append(line.strip("•- "))

    return [l for l in collected if l]


def derive_skills_from_text(raw_text: str, requirements: List[str], tech_section: List[str]) -> Dict[str, List[str]]:
    """
    Dynamically derive skills by analyzing requirement sections and looking for common patterns
    instead of hardcoded sets.
    Categorizes results into 'Languages', 'Technology', 'Experience', and 'Education'.
    """
    languages_list = ["python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust", "php", "sql", "swift", "kotlin", "scala"]
    
    technical = []
    found_languages = []
    found_tech = []
    experience = []
    education = []
    
    candidate_lines = requirements + tech_section
    
    # Common tech patterns: C++, .NET, React.js, AWS, etc.
    tech_pattern = re.compile(r'\b(?:[A-Z][a-zA-Z0-9\+\#\./-]+(?:\s[A-Z][a-zA-Z0-9\+\#\./-]*)*)\b')
    
    # Experience pattern: 3+ years, 5 years, etc.
    exp_pattern = re.compile(r'(\d+[\+]?\s?year[s]?)', re.IGNORECASE)
    
    for line in candidate_lines:
        line_lower = line.lower()
        
        # 1. Tech and Languages
        tech_matches = tech_pattern.findall(line)
        for match in tech_matches:
            if len(match) > 1:
                if match.lower() in languages_list:
                    found_languages.append(match)
                else:
                    found_tech.append(match)
        
        # 2. Experience
        exp_matches = exp_pattern.findall(line)
        for match in exp_matches:
            experience.append(match)
            
        # 3. Education
        if any(keyword in line_lower for keyword in ["degree", "bachelor", "master", "phd", "stem", "university"]):
            education.append(line.strip())

    return {
        "languages": list(dict.fromkeys(found_languages)),
        "technology": list(dict.fromkeys(found_tech)),
        "experience": list(dict.fromkeys(experience)),
        "education": list(dict.fromkeys(education)),
        "soft_skills": ["Teamwork", "Communication", "Problem Solving"] # Simplistic extraction for now or use patterns
    }

def extract_job_type(text: str) -> str:
    text_lower = text.lower()
    if "remote" in text_lower:
        return "Remote"
    elif "hybrid" in text_lower or "days in the office" in text_lower or "days from home" in text_lower:
        return "Hybrid"
    elif "onsite" in text_lower or "on-site" in text_lower or "office" in text_lower:
        return "Onsite"
    return "Onsite" # Default

def extract_skills(text: str) -> tuple[List[str], List[str]]:
    return [], [] # Deprecated


def extract_salary(text: str) -> Optional[str]:
    match = re.search(r"(£|\$|€)\s?\d{2,3}(?:,\d{3})?[kK]?", text)
    return match.group(0) if match else None


# ----------------------------
# Core JD Parsing Logic
# ----------------------------

def parse_job_text(raw_text: str, source_file: str, metadata: Dict = None) -> Dict:
    text_lower = raw_text.lower()
    metadata = metadata or {}

    job: Dict = {
        "raw_text": raw_text,
        "job_title": metadata.get("job_title"),
        "company": metadata.get("company"),
        "location": metadata.get("job_location"),
        "employment_type": None,
        "experience_level": metadata.get("job_level"),
        "technical_skills": [],
        "soft_skills": [],
        "responsibilities": [],
        "requirements": [],
        "education": [],
        "nice_to_have": [],
        "salary": None,
        "source_file": source_file
    }

    # Employment type
    if "intern" in text_lower:
        job["employment_type"] = "Internship"
    elif "contract" in text_lower or re.search(r"\d+\s?months", text_lower):
        job["employment_type"] = "Contract"
    elif "full-time" in text_lower or "full time" in text_lower:
        job["employment_type"] = "Full-time"
    elif metadata.get("job_type"):
        job["employment_type"] = metadata["job_type"]

    # Experience level
    if not job["experience_level"]:
        if "senior" in text_lower:
            job["experience_level"] = "Senior"
        elif "junior" in text_lower:
            job["experience_level"] = "Junior"
        elif "graduate" in text_lower or "entry" in text_lower:
            job["experience_level"] = "Entry"

    # Sections
    job["responsibilities"] = extract_section(raw_text, SECTION_HEADERS["responsibilities"])
    job["requirements"] = extract_section(raw_text, SECTION_HEADERS["requirements"])
    job["education"] = extract_section(raw_text, SECTION_HEADERS["education"])
    job["nice_to_have"] = extract_section(raw_text, SECTION_HEADERS["nice_to_have"])
    tech_sec = extract_section(raw_text, SECTION_HEADERS["technical_skills"])

    # Job Type and Location
    job["employment_type"] = extract_job_type(raw_text)
    if not job["location"]:
        # Simple extraction for location: Canary Wharf, London, etc. often after 'Location:'
        loc_match = re.search(r"Location:\s?([A-Za-z\s]+)", raw_text, re.IGNORECASE)
        if loc_match:
            job["location"] = loc_match.group(1).split('\n')[0].strip()

    # Derived Data
    derived = derive_skills_from_text(raw_text, job["requirements"], tech_sec)
    job["technical_skills"] = derived["technology"]
    job["languages"] = derived["languages"]
    job["experience_required"] = derived["experience"]
    job["education_required"] = derived["education"]
    job["soft_skills"] = [] # Clear old soft skills or move them to nice_to_have

    # Salary
    job["salary"] = extract_salary(raw_text)

    return job


# ----------------------------
# CSV Parsing
# ----------------------------

def parse_job_csv(path: str) -> List[Dict]:
    jobs = []

    with open(path, newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)

        for row in reader:
            raw_text = row.get("job_summary", "") + "\n" + row.get("job_skills", "")
            job = parse_job_text(
                raw_text=raw_text,
                source_file=path,
                metadata=row
            )
            jobs.append(job)

    return jobs


# ----------------------------
# Entry Point
# ----------------------------

def parse_job_description(path: str) -> Union[Dict, List[Dict]]:
    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        return parse_job_csv(path)

    if ext == ".txt":
        raw_text = extract_text_from_txt(path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(path)
    elif ext == ".pdf":
        raw_text = extract_text_from_pdf(path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return parse_job_text(raw_text, source_file=path)


# ----------------------------
# CLI Test
# ----------------------------

if __name__ == "__main__":
    test_file = "../../test_files/job descriptions/postings2.csv"
    # test_file = todo docx, pdf, docx

    data = parse_job_description(test_file)

    from pprint import pprint
    pprint(data, sort_dicts=False)
