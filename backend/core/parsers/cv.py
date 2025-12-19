import os
import re
import pdfplumber
import phonenumbers
import spacy
from collections import defaultdict

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

# Todo later:
#   1. Update skills to be taken from the job description itself
#   2. Update experience parsing to parse as a list of structured experience
#   3. Update education parsing to parse as list of structured education
#   4. Check robustness of link extraction, embedded links, non embedded links, usernames, etc
#   5. Check against different CV formats



# ----------------------------
# Configuration
# ----------------------------

SKILLS = {
    "python", "java", "sql", "aws", "docker", "kubernetes",
    "machine learning", "pandas", "numpy", "tensorflow"
}  # Todo: update this to be taken from JD later

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

    return dict(links_by_source)

def extract_name(text: str):
    doc = nlp(text[:500])  # name usually appears near the top
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_skills(text: str):
    lower = text.lower()
    return [skill for skill in SKILLS if skill in lower]


# ----------------------------
# Section Parsing
# ----------------------------

def split_sections(text: str):
    sections = {"other": []}
    current = "other"

    for line in text.split("\n"):
        line_clean = line.lower().strip()

        if "experience" in line_clean:
            current = "experience"
            sections[current] = []
        elif "education" in line_clean:
            current = "education"
            sections[current] = []
        elif "skills" in line_clean:
            current = "skills"
            sections[current] = []
        else:
            sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items()}


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
        "experience": sections.get("experience"),
        "education": sections.get("education"),
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
