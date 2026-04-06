import os
import re
import csv
import json
from typing import List, Dict, Optional, Union
from docx import Document
from pdfminer.high_level import extract_text

# help find sections in the text
HEADERS = {
    "responsibilities": ["responsibilities", "duties", "what you will do", "role requirements"],
    "requirements": ["requirements", "qualifications", "what we are looking for", "skills", "competencies", "what you will have", "ideal candidate"],
    "technical_skills": ["technical skills", "stack", "tech stack", "technologies"],
    "education": ["education", "degree", "academic", "university"],
    "nice_to_have": ["nice to have", "preferred", "bonus", "desirable"]
}

def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_docx(path):
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def read_pdf(path):
    return extract_text(path)


# ----------------------------- parsing helpers -------------------------------------

def get_section(text, keywords):
    lines = text.splitlines()
    found = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        clean_line = line.strip().lstrip("#").strip() 
        lower_line = clean_line.lower()
        
        # look for a header
        if any(re.search(r'\b' + re.escape(k) + r'\b', lower_line) for k in keywords):

            # consider if the header isnt too long and doesnt seem like a sentence
            if len(clean_line) < 70 and not (clean_line.endswith('.') and len(clean_line) > 40):
                i += 1
                
                while i < len(lines):
                    curr = lines[i]
                    curr_clean = curr.strip()
                    
                    if curr_clean == "":
                        # skip empty lines but check if something big follows
                        if i + 1 < len(lines):
                            nxt = lines[i+1].strip().lstrip("#").strip()
                            if nxt != "" and not lines[i+1].lstrip().startswith(("#", " ", "\t")):
                                # next line looks like a different header
                                if re.match(r"^[A-Z][a-zA-Z\s\-]{2,50}:?$", nxt):
                                     break
                        i += 1
                        continue
                    
                    # stop if we hit another header
                    header_check = curr_clean.lstrip("#").strip()
                    if re.match(r"^[A-Z][a-zA-Z\s\-]{2,50}:?$", header_check) and not (curr.startswith((" ", "\t")) or curr_clean.startswith(("•", "-", "*", "#"))):
                        # if it's not a keyword for THIS section, it's likely a new section
                        if not any(re.search(r'\b' + re.escape(k) + r'\b', header_check.lower()) for k in keywords):
                            break
                    
                    # ignore long sentences that are not bullet pts
                    bullet = curr_clean.startswith(("•", "-", "*", "•", "–")) or curr.startswith(("  ", "\t"))
                    if len(curr_clean) > 300 and not bullet:
                        i += 1
                        continue

                    # clean it up and add it
                    text_line = curr_clean.lstrip("•- *–#").rstrip(":").strip()
                    text_line = text_line.strip("*").strip()
                    if text_line:
                        found.append(text_line)
                    i += 1
                continue
        i += 1
    
    return found


def find_skills(text, reqs, tech, resps=None):
    # figure out what tech they want based on our data file
    data_path = os.path.join(os.path.dirname(__file__), "skills_data.json")
    
    if not os.path.exists(data_path):
        return {"languages": [], "technology": [], "experience": [], "education": []}

    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    langs = set()
    tools = set()
    exp = []
    edu = []
    
    low_text = text.lower()
    
    def match_item(key, source):
        # find the item but watch out for word boundaries
        if any(c in key for c in ["+", "#", "."]):
            return key in source
        return re.search(r'(?<![\w-])' + re.escape(key) + r'(?![\w-])', source)

    # check languages
    seen_langs = set()
    for l in data.get("languages", []):
        low_l = l.lower()
        if low_l not in seen_langs:
            if match_item(low_l, low_text):
                langs.add(l)
                seen_langs.add(low_l)
            
    # check tools/frameworks
    seen_tools = set()
    for t in data.get("frameworks", []):
        low_t = t.lower()
        if low_t not in seen_tools:
            if match_item(low_t, low_text):
                tools.add(t)
                seen_tools.add(low_t)
    
    # pull out years of experience
    yrs = re.findall(r'(\d+(?:\s?-\s?\d+)?[\+]?\s?year[s]?(?:\s?of\s?experience)?)', text, re.IGNORECASE)
    for y in yrs:
        exp.append(y)
        
    # pull out education lines
    edu_keys = ["degree", "bachelor", "master", "phd", "bsc", "msc", "ba", "ma", "diploma", "doctorate"]
    for line in (reqs + (resps or [])):
        if any(re.search(r'\b' + re.escape(k) + r'\b', line.lower()) for k in edu_keys):
            edu.append(line.strip())

    return {
        "languages": sorted(list(langs)),
        "technology": sorted(list(tools)),
        "experience": sorted(list(set(exp))),
        "education": sorted(list(set(edu)))
    }

def get_job_type(text):
    t = text.lower()
    if "remote" in t: return "Remote"
    if "hybrid" in t or "days in the office" in t: return "Hybrid"
    if "onsite" in t or "on-site" in t or "office" in t: return "Onsite"
    return "Onsite"

def get_salary(text):
    p = r"(?:(?:£|\$|€)\s?\d{2,3}(?:,\d{3})?[kK]?\s?(?:[-–]\s?(?:£|\$|€)\s?\d{1,3}(?:,\d{3})?[kK]?)?\s?(?:/day|per day|/yr|per year|/month|per month|annually|per annum|yearly)?)"
    m = re.search(p, text, re.IGNORECASE)
    return m.group(0).strip() if m else None


# ------------------------------- main parsing logic -----------------------------------------

def get_approx_title(text):
    patterns = [
        r"(?:Role|Job|Position|Title):\s*([^\n]+)",
        r"(?:seeking|looking for)\s+a?\s+([A-Z][a-zA-Z\s]*\b(?:Developer|Engineer|Analyst|Scientist|Architect|Lead|Senior|Principal|Manager|Role))\b",
        r"([A-Z][a-zA-Z\s]*\b(?:Developer|Engineer|Analyst|Scientist|Architect)\b)"
    ]
    
    # first few lines usually have the role
    first_lines = text.splitlines()[:15]
    for line in first_lines:
        clean = line.strip().lstrip("#").strip().strip("= -*").rstrip(":").strip()
        
        # empty line
        if not clean: 
            continue

        # likely a title if short and has keywords
        if len(clean) < 70 and any(kw in clean.lower() for kw in ["developer", "engineer", "analyst", "scientist", "architect", "lead", "senior", "role"]):
            return clean

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def get_approx_company(text):
    m = re.search(r"(?:About Us|About|Company Description|The Company|ABOUT)\s*(?:[-=:\s]|\n)+\s*([A-Z][a-zA-Z0-9]*(?:[ \t]+[A-Z][a-zA-Z0-9]*)*)", text, re.IGNORECASE)
    if m:
        name = m.group(1).strip().strip('= -').strip()
        if name.lower() not in ["the job", "this role", "us", "the company", "tech corp", "this"]:
             return name
             
    first_500 = text[:1000]
    m = re.search(r"([A-Z][a-zA-Z0-9]+(?:[ \t]+[A-Z][a-zA-Z0-9]+)*)\s+(?:has|is|was)\s+(?:celebrated|a|seeking|founded)", first_500)
    if m:
        name = m.group(1).strip()
        if name.lower() not in ["this"]:
            return name
    return None

def parse_job(text, source_file, meta=None):
    low_text = text.lower()
    meta = meta or {}

    res = {
        "raw_text": text,
        "job_title": meta.get("job_title") or get_approx_title(text),
        "company": meta.get("company") or get_approx_company(text),
        "location": meta.get("job_location"),
        "employment_type": None,
        "experience_level": meta.get("job_level"),
        "technical_skills": [],
        "soft_skills": [],
        "responsibilities": [],
        "requirements": [],
        "education": [],
        "nice_to_have": [],
        "salary": None,
        "source_file": source_file
    }

    # guess employment type
    if "intern" in low_text:
        res["employment_type"] = "Internship"
    elif "contract" in low_text or re.search(r"\d+\s?months", low_text):
        res["employment_type"] = "Contract"
    elif "full-time" in low_text or "full time" in low_text:
        res["employment_type"] = "Full-time"
    elif "hybrid" in low_text:
        res["employment_type"] = "Hybrid"
    elif "remote" in low_text:
        res["employment_type"] = "Remote"
    elif meta.get("job_type"):
        res["employment_type"] = meta["job_type"]

    # guess experience level
    if not res["experience_level"]:
        if re.search(r"\bintern(ship)?\b", low_text):
            res["experience_level"] = "Internship"
        elif re.search(r"\bsenior\b|\blead\b|\bstaff\b|\bprincipal\b", low_text):
            res["experience_level"] = "Senior"
        elif re.search(r"\bmid\b|\bintermediate\b", low_text):
            res["experience_level"] = "Mid"
        elif re.search(r"\bjunior\b", low_text):
            res["experience_level"] = "Junior"
        elif re.search(r"\bgraduate\b|\bentry\b", low_text):
            res["experience_level"] = "Entry"

    # location estimation
    if not res["location"]:
        m = re.search(r"Location:\s?([A-Za-z\s]+)", text, re.IGNORECASE)
        if m:
            res["location"] = m.group(1).split('\n')[0].strip()
        elif "London" in text:
            res["location"] = "London, UK"

    # pull sections
    res_sec = get_section(text, HEADERS["responsibilities"])
    req_sec = get_section(text, HEADERS["requirements"])
    edu_sec = get_section(text, HEADERS["education"])
    nic_sec = get_section(text, HEADERS["nice_to_have"])
    tec_sec = get_section(text, HEADERS["technical_skills"])

    res["responsibilities"] = res_sec
    res["requirements"] = req_sec
    res["education"] = edu_sec
    res["nice_to_have"] = nic_sec
    
    # compute skills
    skills = find_skills(text, req_sec + res_sec + nic_sec, tec_sec)
    res["technical_skills"] = sorted(list(set(skills["technology"])))
    res["languages"] = sorted(list(set(skills["languages"])))
    res["experience_required"] = sorted(list(set(skills["experience"])))
    res["education_required"] = sorted(list(set(skills["education"])))
    res["salary"] = get_salary(text)

    return res


def parse_jd(path, meta=None):
    ext = os.path.splitext(path)[1].lower()

    if ext in [".txt", ".md"]:
        raw = read_txt(path)
    elif ext == ".docx":
        raw = read_docx(path)
    elif ext == ".pdf":
        raw = read_pdf(path)
    else:
        raise ValueError(f"unsupported file extension: {ext}")

    return parse_job(raw, path, meta=meta)
