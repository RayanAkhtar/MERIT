import os
import requests
from typing import Dict, Optional


APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

print(f"[LinkedIn] Provider Config: Apify={'SET' if APIFY_API_TOKEN else 'MISSING'}")

if not APIFY_API_TOKEN:
    raise RuntimeError("No LinkedIn API keys found in .env")

def extract_linkedin_id(profile_url: str) -> str:
    """https://www.linkedin.com/in/john-smith/ -> john-smith"""
    return profile_url.rstrip("/").split("/")[-1]


def safe_json(response: requests.Response) -> Optional[Dict]:
    """parses json, if it fails, it returns None instead"""
    try:
        return response.json()
    except ValueError:
        print("Non-JSON response received:")
        print(response.text[:500])
        return None


def linkedin_person_scrape(linkedin_url: str) -> Optional[Dict]:
    """Scrape LinkedIn profile using Apify."""

    if APIFY_API_TOKEN:
        print(f"[LinkedIn] Attempting Deep Scrape via Apify for: {linkedin_url}")
        apify_endpoint = f"https://api.apify.com/v2/acts/harvestapi~linkedin-profile-scraper/run-sync-get-dataset-items?token={APIFY_API_TOKEN}"
        
        payload = {
            "urls": [linkedin_url],
            "profileScraperMode": "Profile details no email ($4 per 1k)",
            "proxy": { "useApifyProxy": True }
        }

        try:
            response = requests.post(apify_endpoint, json=payload, timeout=120)
            if response.status_code == 201 or response.status_code == 200:
                data = safe_json(response)
                if isinstance(data, list) and len(data) > 0:
                    print("[LinkedIn] Apify success")
                    res = data[0]
                    res["provider"] = "apify"
                    return res
            print(f"[LinkedIn] Apify failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"[LinkedIn] Apify exception: {str(e)}")

    return None


def parse_linkedin_profile(data):
    if not data:
        return {}

    provider = data.get("provider", "apify")
    profile = {}

    if provider == "apify":
        profile["full_name"] = data.get("fullName") or f"{data.get('firstName', '')} {data.get('lastName', '')}".strip()
        profile["first_name"] = data.get("firstName")
        profile["last_name"] = data.get("lastName")
        profile["headline"] = data.get("headline")
        profile["location"] = data.get("location")
        profile["followers"] = data.get("followersCount")
        profile["connections"] = data.get("connectionsCount")
        profile["about"] = data.get("about") or data.get("summary")
        profile["profile_photo"] = data.get("profilePicUrl") or data.get("profilePhoto")
        profile["background_image"] = data.get("backgroundPicUrl")

        profile["experience"] = []
        exp_list = data.get("experience") or data.get("positionHistory") or []
        for exp in exp_list:
            profile["experience"].append({
                "company_name": exp.get("companyName") or exp.get("company"),
                "company_image": exp.get("companyLogoUrl"),
                "position": exp.get("title") or exp.get("position"),
                "start_date": exp.get("startDateText") or exp.get("startDate"),
                "end_date": exp.get("endDateText") or exp.get("endDate") or "Present",
                "description": exp.get("description"),
                "skills": [s.get("name") if isinstance(s, dict) else str(s) for s in (exp.get("skills") or []) if s]
            })


        profile["education"] = []
        edu_list = data.get("education") or data.get("schools") or []
        for edu in edu_list:
            profile["education"].append({
                "school_name": edu.get("schoolName") or edu.get("school") or edu.get("schoolName"),
                "degree": edu.get("degreeName") or edu.get("degree"),
                "start_date": edu.get("startDateText") or edu.get("startDate"),
                "end_date": edu.get("endDateText") or edu.get("endDate"),
                "field_of_study": edu.get("fieldOfStudy")
            })


        profile["volunteering"] = []
        vol_list = data.get("volunteering") or data.get("volunteerExperiences") or []
        for vol in vol_list:
            profile["volunteering"].append({
                "position": vol.get("title") or vol.get("role"),
                "organization": vol.get("companyName") or vol.get("organization"),
                "start_date": vol.get("startDateText"),
                "end_date": vol.get("endDateText"),
                "url": vol.get("companyUrl")
            })


        profile["projects"] = []
        for proj in (data.get("projects") or []):
            title = proj.get("title")
            if title:
                start_obj = proj.get("startDate") or {}
                end_obj = proj.get("endDate") or {}
                profile["projects"].append({
                    "title": title,
                    "start_date": start_obj.get("text") or start_obj.get("year"),
                    "end_date": end_obj.get("text") or end_obj.get("year") or "N/A",
                    "duration": proj.get("dateText") or "N/A",
                    "description": proj.get("description")
                })

        profile["certifications"] = []
        for cert in (data.get("certifications") or []):
            profile["certifications"].append({
                "title": cert.get("name") or cert.get("title"),
                "issuer": cert.get("authority") or cert.get("issuer"),
                "issue_date": cert.get("dateText"),
                "credential_url": cert.get("url")
            })
        return profile

    return {}


def pretty_print(data, indent=0):
    spacing = " " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            print(f"{spacing}{k}:")
            pretty_print(v, indent + 2)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            print(f"{spacing}- [{i}]")
            pretty_print(item, indent + 2)
    else:
        print(f"{spacing}{data}")
