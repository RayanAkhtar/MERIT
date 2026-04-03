import os
import re
import json
import pdfplumber
import phonenumbers
import spacy
from collections import defaultdict

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

# ----------------------------
# Skill Data Ingestion
# ----------------------------

def load_skills_from_json():
    """
    Dynamically loads technical markers from the centralized skills_data.json.
    Merges all categories into a single searchable set.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        skills_path = os.path.join(current_dir, "skills_data.json")
        
        if not os.path.exists(skills_path):
            print(f"WARNING: skills_data.json not found at {skills_path}. Using fallback skills.")
            return {"python", "javascript", "react", "node", "sql", "java", "aws", "docker"}

        with open(skills_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            combined_skills = set()
            for category in data.values():
                if isinstance(category, list):
                    for skill in category:
                        combined_skills.add(skill.lower())
            
            return combined_skills
    except Exception as e:
        print(f"WARNING: Failed to ingest skills_data.json: {str(e)}")
        return {"python", "javascript", "react", "node", "sql"}

# Globally active skill vocabulary
SKILLS = load_skills_from_json()

LINK_PATTERNS = {
    "linkedin": re.compile(r"linkedin\.com", re.IGNORECASE),
    "github": re.compile(r"github\.com", re.IGNORECASE),
    "gitlab": re.compile(r"gitlab\.com", re.IGNORECASE)
}


nlp = spacy.load("en_core_web_sm")


# ----------------------------
# File Extraction
# ----------------------------

def extract_text_and_links_from_pdf(path: str):
    text = []
    links = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)

            # Extract embedded hyperlinks
            if page.annots:
                for annot in page.annots:
                    uri = annot.get("uri")
                    if uri:
                        links.append(uri)

    return "\n".join(text), links


def extract_text_and_links_from_docx(path: str):
    doc = Document(path)

    text = []
    links = []

    # Extract visible text
    for p in doc.paragraphs:
        text.append(p.text)

    # Extract embedded hyperlinks
    for rel in doc.part.rels.values():
        if rel.reltype == RT.HYPERLINK:
            links.append(rel.target_ref)

    return "\n".join(text), links


def extract_text_and_links(path: str):
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        return extract_text_and_links_from_pdf(path)
    elif ext == ".docx":
        return extract_text_and_links_from_docx(path)
    else:
        raise ValueError("Unsupported file format")


# ----------------------------
# Text Utilities
# ----------------------------

def clean_text(text: str):
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ----------------------------
# Field Extraction
# ----------------------------

def extract_email(text: str):
    match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return match.group(0) if match else None


def extract_phone(text: str):
    for match in phonenumbers.PhoneNumberMatcher(text, None):
        return phonenumbers.format_number(
            match.number,
            phonenumbers.PhoneNumberFormat.E164
        )
    return None


def extract_links(text: str, embedded_links=None):
    links_by_source = defaultdict(list)

    # 1. Visible URLs
    visible_links = re.findall(r"https?://\S+", text)

    # 2. Combine all links
    all_links = set(visible_links)
    if embedded_links:
        all_links.update(embedded_links)

    # 3. Filter + classify
    for url in all_links:
        # Skip mailto links
        if url.lower().startswith("mailto:"):
            continue

        matched = False
        for source, pattern in LINK_PATTERNS.items():
            if pattern.search(url):
                links_by_source[source].append(url)
                matched = True
                break

        if not matched:
            links_by_source["other"].append(url)

    # 4. Keyword-based extraction for usernames (if not already found via URL)
    if not links_by_source["linkedin"]:
        linkedin_match = re.search(r"LinkedIn:\s*([\w\-\.]+)", text, re.IGNORECASE)
        if linkedin_match:
            username = linkedin_match.group(1)
            links_by_source["linkedin"].append(f"https://linkedin.com/in/{username}")

    if not links_by_source["github"]:
        github_match = re.search(r"GitHub:\s*([\w\-\.]+)", text, re.IGNORECASE)
        if github_match:
            username = github_match.group(1)
            links_by_source["github"].append(f"https://github.com/{username}")

    return dict(links_by_source)

def extract_name(text: str):
    doc = nlp(text[:500])  # name usually appears near the top
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_skills(text: str):
    """
    Extracts specialized skills using boundary-aware regex to prevent false positives.
    (e.g., prevents 'going' from being flagged as the language 'Go').
    """
    lower = text.lower()
    found_skills = set()
    
    for skill in SKILLS:
        skill_clean = skill.lower()
        # Create a dynamic pattern: use word boundaries \b for alphanumeric starts/ends 
        # to prevent substring collisions, but allow symbols like C++ or .NET
        pattern = ""
        
        # Leading boundary: only if the skill starts with a word character
        if skill_clean[0].isalnum():
            pattern += r"\b"
        pattern += re.escape(skill_clean)
        # Trailing boundary: only if the skill ends with a word character
        if skill_clean[-1].isalnum():
            pattern += r"\b"
            
        if re.search(pattern, lower):
            found_skills.add(skill)
            
    return sorted(list(found_skills))


# ----------------------------
# Section Parsing
# ----------------------------

def split_sections(text: str):
    sections = {"other": []}
    current = "other"
    
    # Common headers and their variations
    HEADERS_MAP = {
        "experience": ["experience", "work history", "employment", "professional experience"],
        "education": ["education", "academic", "qualifications", "background"],
        "projects": ["projects", "personal projects", "technical projects", "academic projects"],
        "extracurricular": ["extracurricular", "volunteer", "activities", "leadership", "community"],
        "skills": ["skills", "technical skills", "expertise", "competencies"]
    }

    for line in text.split("\n"):
        line_strip = line.strip()
        if not line_strip: continue
        
        line_clean = line_strip.lower()
        
        # Heuristic for header: short line (<= 4 words) that matches a section pattern
        is_header = False
        words = line_strip.split()
        if len(words) <= 4:
            for section, patterns in HEADERS_MAP.items():
                if any(p == line_clean or line_clean.startswith(p + " ") for p in patterns):
                    # headers are typically uppercase OR start with uppercase and are single words/short
                    if line_strip.isupper() or (len(words) == 1 and line_strip[0].isupper()):
                        current = section
                        if current not in sections:
                            sections[current] = []
                        is_header = True
                        break
        
        if not is_header:
            sections[current].append(line_strip)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


def extract_structured_section(text: str, section_key: str):
    # Generalized helper for sections with "Name | Subtitle" format (Projects, Extracurricular, etc.)
    sections = split_sections(text)
    section_text = sections.get(section_key, "")
    if not section_text:
        return []

    items = []
    lines = section_text.split("\n")
    current_item = None

    for line in lines:
        line = line.strip()
        if not line: continue

        # Header detection: pipe separator is a very strong signal for structured items
        if "|" in line:
            if current_item:
                items.append(current_item)
            
            parts = line.split("|")
            name = parts[0].strip()
            rest = parts[1].strip()
            
            # Robust tech stack/role extraction: split on date patterns
            # Only match actual month names/abbreviations to avoid cutting off course names like "Computer Science"
            months = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            date_pattern = rf'\s+(?:{months}\s+)?(?:[12][0-9]{3})(?:\s*-\s*(?:Present|{months}\s+)?(?:[12][0-9]{3})?)?'
            subtitle = re.split(date_pattern, rest)[0].strip()

            current_item = {
                "name": name,
                "subtitle": subtitle,
                "summary": ""
            }
        elif (line.startswith("•") or line.startswith("-") or line.startswith("*")) and current_item:
            bullet_text = line.lstrip("•-* ").strip()
            if not current_item["summary"]:
                current_item["summary"] = bullet_text
            elif len(current_item["summary"]) < 180: # Aggregated summary for better context
                current_item["summary"] += " " + bullet_text
    
    if current_item:
        items.append(current_item)

    return items


# ----------------------------
# Main Parser
# ----------------------------

def parse_cv(path: str):
    raw_text, embedded_links = extract_text_and_links(path)
    cleaned_text = clean_text(raw_text)
    sections = split_sections(raw_text)

    return {
        "name": extract_name(cleaned_text),
        "email": extract_email(cleaned_text),
        "phone": extract_phone(cleaned_text),
        "links": extract_links(cleaned_text, embedded_links),
        "skills": extract_skills(cleaned_text),
        "projects": extract_structured_section(raw_text, "projects"),
        "extracurricular": extract_structured_section(raw_text, "extracurricular"),
        "experience": sections.get("experience"),
        "education": extract_structured_section(raw_text, "education"),
    }

def get_available_links(path: str):
    raw_text, embedded_links = extract_text_and_links(path)
    cleaned_text = clean_text(raw_text)

    # Extract links and return True/False for each occurrence
    links = extract_links(cleaned_text, embedded_links)
    return {key: bool(value) for key, value in links.items()}

# ----------------------------
# Entry Point
# ----------------------------

if __name__ == "__main__":
    cv_path = "test_files/Rayan Akhtar's CV.pdf"
    parsed_data = parse_cv(cv_path)

    for key, value in parsed_data.items():
        print(f"{key}: {value}\n")
