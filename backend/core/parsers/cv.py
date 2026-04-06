import os
import re
import json
import pdfplumber
import phonenumbers
import spacy
from collections import defaultdict

from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def load_skills_from_json():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    skills_path = os.path.join(current_dir, "skills_data.json")

    with open(skills_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        combined_skills = set()
        for category in data.values():
            if isinstance(category, list):
                for skill in category:
                    combined_skills.add(skill.lower())
        
        return combined_skills

SKILLS = load_skills_from_json()

LINK_PATTERNS = {
    "linkedin": re.compile(r"linkedin\.com", re.IGNORECASE),
    "github": re.compile(r"github\.com", re.IGNORECASE),
    "gitlab": re.compile(r"gitlab\.com", re.IGNORECASE)
}

nlp = spacy.load("en_core_web_sm")



def extract_text_and_links_from_pdf(path: str):
    text = []
    links = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            
            if page_text:
                text.append(page_text)

            # embedded hyperlinks
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

    # visible text
    for p in doc.paragraphs:
        text.append(p.text)

    # embedded hyperlinks
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


def clean_text(text: str):
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


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

    visible_links = re.findall(r"https?://\S+", text)
    all_links = set(visible_links)

    if embedded_links:
        all_links.update(embedded_links)

    # filter + classify links
    for url in all_links:
        # skipping email links since they are not data sources
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
    doc = nlp(text[:500])  
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_skills(text: str):
    lower = text.lower()
    found_skills = set()
    
    for skill in SKILLS:
        skill_clean = skill.lower()
        # using word boundaries \b for alphanumeric starts/ends 
        # to prevent substring collisions
        pattern = ""
        
        # if the skill starts with a word character
        if skill_clean[0].isalnum():
            pattern += r"\b"
        pattern += re.escape(skill_clean)

        # if the skill ends with a word character
        if skill_clean[-1].isalnum():
            pattern += r"\b"
            
        # if the pattern is found in the text, add the skill to the set
        if re.search(pattern, lower):
            found_skills.add(skill)
            
    return sorted(list(found_skills))


# ------------------------------------------------------------------------------------
# Section Parsing
# ------------------------------------------------------------------------------------

def split_sections(text: str):
    sections = {"other": []}
    current = "other"
    
    # common headers and their variations, its a very crude implementation
    # but for this project, it should be fine
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
        
        # heuristic for header: short line (<= 4 words) that matches a section pattern
        is_header = False
        words = line_strip.split()

        if len(words) <= 4:
            for section, patterns in HEADERS_MAP.items():
                if any(p == line_clean or line_clean.startswith(p + " ") for p in patterns):
                    # headers are short and usually capped or stylised
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
    # helper for sections with "Name | Subtitle" format (Projects, Extracurricular, etc.)
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

        # pipe separator commonly used in structured items
        if "|" in line:
            if current_item:
                items.append(current_item)
            
            parts = line.split("|")
            name = parts[0].strip()
            rest = parts[1].strip()
            
            # date fingerprinting
            # currently matches ranges like:
            #  "Oct 2024 – Nov 2024"
            #  "2022-2023",
            #  "Present"
            months_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            
            # year is 4 digits from 1900-2999
            year_pattern = r'[12][0-9]{3}'
            
            # date part
            # currently matches ranges like:
            #   Month Year
            #   Year
            date_part = rf'(?:(?:{months_pattern}\s+)?{year_pattern})'
            
            # Common dashes:
            # \- (hyphen)
            # \u2013 (en dash)
            # \u2014 (em dash)
            dash_pattern = r'[\-\u2013\u2014\.\/]'
            
            # extracting date range from the subtitle
            # Matches regex: (Expected )?(DatePart)(Dash)(DatePart or Present/Current/Ongoing)
            range_regex = rf'(?:Expected\s+)?({date_part})\s*{dash_pattern}+\s*({date_part}|Present|Current|Ongoing|Now)'
            
            # Matches regex: (Expected )?(DatePart)
            single_regex = rf'(?:Expected\s+)?({date_part})'
            
            date_match = re.search(range_regex, rest, re.IGNORECASE)
            if date_match:
                start_date = date_match.group(1).strip()
                end_date = date_match.group(2).strip()
                full_date_match = date_match.group(0)
            else:
                single_match = re.search(single_regex, rest, re.IGNORECASE)
                start_date = single_match.group(1).strip() if single_match else None
                end_date = None
                full_date_match = single_match.group(0) if single_match else ""
            
            # extract subtitle
            if full_date_match:
                cleaned_subtitle = rest.replace(full_date_match, "").strip().rstrip(",- ").strip()
            else:
                cleaned_subtitle = rest
            
            # extract grade from subtitle
            grade = None
            grade_patterns = [
                r'(?:Expected\s+)?(?:First|Second|Third|1st|2nd|3rd)\s+Class(?:\s+Honours)?',
                r'[12]:[12](?:\s+Honours)?',
                r'GPA\s*[\d\.]+(?:/\d\.\d)?',
                r'Distinction|Merit|Pass',
                r'\d{2}%\s+Average',
            ]
            
            for pattern in grade_patterns:
                g_match = re.search(pattern, cleaned_subtitle, re.IGNORECASE)
                if g_match:
                    grade = g_match.group(0).strip()

                    # strip the grade from the degree title
                    cleaned_subtitle = cleaned_subtitle.replace(grade, "").strip().rstrip(",- ").strip()
                    break

            current_item = {
                "name": name,
                "subtitle": cleaned_subtitle,
                "start_date": start_date,
                "end_date": end_date,
                "grade": grade,
                "summary": ""
            }

        # if the line starts with a bullet point, add it to the current item's summary
        elif (line.startswith("•") or line.startswith("-") or line.startswith("*")) and current_item:
            bullet_text = line.lstrip("•-* ").strip()
            
            # if grade is not found in the title
            if not current_item["grade"]:
                grade_match = re.search(r'(grade|gpa|classification|result|grade achieved):\s*([\w\+\.\s/]+)', bullet_text, re.IGNORECASE)
                if grade_match:
                    current_item["grade"] = grade_match.group(2).strip()
                elif "first class" in bullet_text.lower() or "distinction" in bullet_text.lower():
                     current_item["grade"] = bullet_text if len(bullet_text) < 40 else bullet_text[:40]

            if not current_item["summary"]:
                current_item["summary"] = bullet_text
            elif len(current_item["summary"]) < 180:
                current_item["summary"] += " " + bullet_text
    
    if current_item:
        items.append(current_item)

    return items


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

    links = extract_links(cleaned_text, embedded_links)
    return {key: bool(value) for key, value in links.items()}
