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
# Skill Dictionaries
# ----------------------------

# TODO START: update this to be dynamic instead

TECHNICAL_SKILLS = {
    "python", "java", "javascript", "typescript", "c++", "c",
    "sql", "nosql", "mongodb", "postgresql",
    "react", "node", "express", "django", "flask",
    "aws", "gcp", "azure", "docker", "kubernetes",
    "linux", "git", "github",
    "machine learning", "deep learning", "nlp",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "rest", "graphql"
}

SOFT_SKILLS = {
    "communication", "teamwork", "collaboration",
    "problem solving", "problem-solving",
    "leadership", "initiative",
    "time management", "adaptability",
    "critical thinking", "organisation", "organization",
    "attention to detail", "work ethic"
}

SECTION_HEADERS = {
    "responsibilities": ["responsibilities", "role", "what you will do"],
    "requirements": ["requirements", "qualifications", "what we are looking for"],
    "education": ["education", "degree", "academic"],
    "nice_to_have": ["nice to have", "preferred", "bonus"]
}
# TODO END: up till here

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


def extract_skills(text: str) -> tuple[List[str], List[str]]:
    text_lower = text.lower()

    technical = {s for s in TECHNICAL_SKILLS if s in text_lower}
    soft = {s for s in SOFT_SKILLS if s in text_lower}

    return sorted(technical), sorted(soft)


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
    elif "contract" in text_lower:
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

    # Skills
    tech, soft = extract_skills(raw_text)
    job["technical_skills"] = tech
    job["soft_skills"] = soft

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
