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

    # If we still don't have links, try a basic regex for usernames
    # This is a bit hit or miss but works for some formats
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
        # this regex took a lot of tweaking to stop 'C' matching everything
        if re.search(pattern, lower):
            found_skills.add(skill)
            
    return sorted(list(found_skills))


# ------------------------------------------------------------------------------------
# Section Parsing
# ------------------------------------------------------------------------------------

def split_sections(text: str):
    sections = {"other": []}
    current = "other"
    
    # common headers and their variations (a very crude implementation)
    # but for this project, should be fine
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
    sections = split_sections(text)
    section_text = sections.get(section_key, "")
    if not section_text:
        return []

    # Load High-Confidence Universities
    current_dir = os.path.dirname(os.path.abspath(__file__))
    uni_path = os.path.join(current_dir, "universities_data.json")
    try:
        with open(uni_path, "r") as f:
            UNI_DATA = json.load(f).get("uk_universities", [])
    except:
        UNI_DATA = []

    items = []
    lines = section_text.split("\n")
    current_item = None

    # High-Confidence Universities in the UK (mostly London ones for testing)
    INST_KEYWORDS = ["university", "college", "imperial", "institute", "polytechnic", "london academy", "ucl", "lse", "kcl"]
    DEGREE_KEYWORDS = ["beng", "meng", "bsc", "msc", "msci", "phd", "ba", "ma", "bachelor", "master", "doctor", "postgraduate", "undergraduate"]
    
    # Junk keywords that signify NOT a header
    JUNK_HEADERS = ["module", "key module", "achieved", "ranked", "award", "scholarship", "project", "skill", "subject", "expected", "grade", "results"]

    for line in lines:
        line = line.strip()
        if not line: continue

        line_lower = line.lower()
        
        # flexible separator check (Pipe, Comma, or Colon)
        separator = None
        if "|" in line: separator = "|"
        elif "," in line and section_key == "education": separator = "," # Commas common in education
        elif ":" in line: separator = ":"
        
        # section-Specific Header Detection
        # print(f"DEBUG - {line}")
        is_new_header = False
        if section_key == "education":
            # Education headers can be long if they include grades/dates/locations
            is_bullet = line.startswith(("•", "-", "*", "•"))
            starts_with_junk = any(line_lower.startswith(jk) for jk in JUNK_HEADERS)
            has_degree = any(dk in line_lower for dk in DEGREE_KEYWORDS)
            has_known_uni = any(uk.lower() in line_lower for uk in UNI_DATA) or any(ik in line_lower for ik in INST_KEYWORDS)
            
            # Heuristic: If it has a degree keyword, it's almost certainly a header, even if it has junk
            if (not is_bullet) and (has_degree or (not starts_with_junk and has_known_uni)) and len(line.split()) < 25:
                is_new_header = True
        else:
            # Relaxed logic for Projects/Extracurricular/Experience
            # Usually Name | Subtitle or Name: Subtitle
            # We look for a separator or a short line that looks like a title
            if (separator or len(line.split()) < 7) and not line.startswith(("•", "-", "*")):
                is_new_header = True

        if is_new_header:
            if current_item:
                items.append(current_item)
            
            # Split logic
            name = line
            subtitle = ""
            
            if separator:
                parts = line.split(separator, 1)
                p1, p2 = parts[0].strip(), parts[1].strip()
                
                if section_key == "education":
                    p1_is_inst = any(k in p1.lower() for k in INST_KEYWORDS + UNI_DATA)
                    p2_is_deg = any(k in p2.lower() for k in DEGREE_KEYWORDS)
                    if p1_is_inst: name, subtitle = p1, p2
                    elif p2_is_deg: name, subtitle = p1, p2
                    else: name, subtitle = p1, p2
                else:
                    name, subtitle = p1, p2
            else:
                # No separator but both institution and degree might be in the same string (Education Only)
                if section_key == "education":
                    for deg in DEGREE_KEYWORDS:
                        if f" {deg}" in f" {line_lower}":
                            start_idx = line_lower.find(deg)
                            name = line[:start_idx].strip().rstrip(",- ").strip()
                            subtitle = line[start_idx:].strip()
                            break

            # Extraction for date/grade (Common to all sections)
            months_pattern = r'(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)'
            year_pattern = r'[12][0-9]{3}'
            date_part = rf'(?:(?:{months_pattern}\s+)?{year_pattern})'
            dash_pattern = r'[\-\u2013\u2014\.\/]'
            range_regex = rf'(?:Expected\s+)?({date_part})\s*{dash_pattern}+\s*({date_part}|Present|Current|Ongoing|Now)'
            single_regex = rf'(?:Expected\s+)?({date_part})'
            
            date_match = re.search(range_regex, line, re.IGNORECASE)
            start_date, end_date, full_date_match = None, None, ""
            if date_match:
                start_date, end_date, full_date_match = date_match.group(1).strip(), date_match.group(2).strip(), date_match.group(0)
            else:
                single_match = re.search(single_regex, line, re.IGNORECASE)
                if single_match:
                    start_date, full_date_match = single_match.group(1).strip(), single_match.group(0)

            if full_date_match:
                name = name.replace(full_date_match, "").strip().rstrip(",- ").strip()
                subtitle = subtitle.replace(full_date_match, "").strip().rstrip(",- ").strip()

            grade = None
            grade_patterns = [
                r'(?:On\s+track\s+for\s+)?(?:First|Second|Third|1st|2nd|3rd)\s+Class(?:\s+Honours)?',
                r'(?:Expected\s+)?(?:First|Second|Third|1st|2nd|3rd)\s+Class(?:\s+Honours)?',
                r'[12]:[12](?:\s+Honours)?', r'GPA\s*[\d\.]+(?:/\d\.\d)?',
                r'Distinction|Merit|Pass', r'\d{2}%\s+Average',
                r'A\*s?\s+in\s+All\s+Subjects', r'A\*A\*A\*A\*?'
            ]
            for pattern in grade_patterns:
                g_match = re.search(pattern, line, re.IGNORECASE)
                if g_match:
                    grade = g_match.group(0).strip()
                    subtitle = subtitle.replace(grade, "").strip().rstrip(",- ").strip()
                    name = name.replace(grade, "").strip().rstrip(",- ").strip()
                    break

            current_item = {"name": name, "subtitle": subtitle, "start_date": start_date, "end_date": end_date, "grade": grade, "summary": ""}

        elif (line.startswith("•") or line.startswith("-") or line.startswith("*")) and current_item:
            bullet_text = line.lstrip("•-* ").strip()
            if not current_item["grade"]:
                grade_match = re.search(r'(grade|gpa|classification|result|grade achieved):\s*([\w\+\.\s/]+)', bullet_text, re.IGNORECASE)
                if grade_match: current_item["grade"] = grade_match.group(2).strip()
                elif "first class" in bullet_text.lower() or "distinction" in bullet_text.lower():
                     current_item["grade"] = bullet_text if len(bullet_text) < 40 else bullet_text[:40]
            if not current_item["summary"]: current_item["summary"] = bullet_text
            elif len(current_item["summary"]) < 180: current_item["summary"] += " " + bullet_text
    
    if current_item:
        items.append(current_item)

    # Stricter Filter: Must look like a real University Degree
    if section_key == "education":
        filtered_items = []
        SCHOOL_LEVEL_KEYWORDS = ["a-level", "gcse", "a level", "sixth form", "junior", "secondary", "grammar", "high school", "highschool", "boys", "girls"]

        for item in items:
            combined = (item["name"] + " " + item["subtitle"]).lower()
            is_degree = any(dk in combined for dk in DEGREE_KEYWORDS)
            is_school = any(sk in combined for sk in SCHOOL_LEVEL_KEYWORDS)
            
            # keep if it's a degree AND doesn't look like a high-school entry
            # print(f"DEBUG: {item['name']} - is_degree: {is_degree}, is_school: {is_school}")
            if is_degree and not is_school:
                filtered_items.append(item)
        
        return filtered_items

        return filtered_items

    # Fallback for other sections
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
        "cv_experience": extract_structured_section(raw_text, "experience"),
        "experience": sections.get("experience"), # Keep raw text for density/text analysis
        "education": extract_structured_section(raw_text, "education"),
    }

def get_available_links(path: str):
    raw_text, embedded_links = extract_text_and_links(path)
    cleaned_text = clean_text(raw_text)

    links = extract_links(cleaned_text, embedded_links)
    return {key: bool(value) for key, value in links.items()}
