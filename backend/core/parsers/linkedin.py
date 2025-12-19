import os
import time
import requests
from typing import Dict, Optional

# TODO:
#   1. See if scrapingdog can be done cheaper, scraping less details if possible
#   2. Consider whether pictures should be kept in this scraper?
#   3. Also consider removing unneeded stuff so we can save space
#


# Currently the following structure
# {
#     "full_name": str,
#     "first_name": str,
#     "last_name": str,
#     "headline": str,
#     "location": str,
#     "followers": str,
#     "connections": str,
#     "about": str,
#     "profile_photo": str (URL),
#     "background_image": str (URL),
#     "experience": [             # list of dicts
#         {
#             "company_name": str,
#             "company_image": str (URL),
#             "position": str,
#             "start_date": str,
#             "end_date": str
#         },
#         ...
#     ],
#     "education": [              # list of dicts
#         {
#             "school_name": str,
#             "degree": str,
#             "start_date": str,
#             "end_date": str
#         },
#         ...
#     ],
#     "volunteering": [           # list of dicts
#         {
#             "position": str,
#             "organization": str,
#             "start_date": str,
#             "end_date": str,
#             "url": str
#         },
#         ...
#     ],
#     "projects": [               # list of dicts
#         {
#             "title": str,
#             "link": str,
#             "duration": str
#         },
#         ...
#     ],
#     "certifications": [         # list of dicts
#         {
#             "title": str,
#             "issuer": str,
#             "issue_date": str,
#             "credential_url": str
#         },
#         ...
#     ],
#     "languages": [              # list of dicts
#         {
#             "name": str,
#             "level": str
#         },
#         ...
#     ],
#     "activities": [             # list of dicts
#         {
#             "title": str,
#             "link": str,
#             "activity_type": str
#         },
#         ...
#     ],
# }





# ----------------------------------
# Configuration
# ----------------------------------

SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
SCRAPINGDOG_PROFILE_ENDPOINT = "https://api.scrapingdog.com/profile"

if not SCRAPINGDOG_API_KEY:
    raise RuntimeError("SCRAPINGDOG_API_KEY environment variable not set")

# ----------------------------------
# Helpers
# ----------------------------------

def extract_linkedin_id(profile_url: str) -> str:
    """
    Extract LinkedIn public identifier from profile URL
    Example:
    https://www.linkedin.com/in/rayan-akhtar/ -> rayan-akhtar
    """
    return profile_url.rstrip("/").split("/")[-1]


def safe_json(response: requests.Response) -> Optional[Dict]:
    """
    Safely parse JSON, return None if response is not JSON
    """
    try:
        return response.json()
    except ValueError:
        print("Non-JSON response received:")
        print(response.text[:500])
        return None


# ----------------------------------
# Core Scraper
# ----------------------------------

def linkedin_person_scrape(
    linkedin_url: str,
    premium: bool = True,
    retries: int = 3,
    wait_seconds: int = 10
) -> Optional[Dict]:
    """
    Scrape LinkedIn profile via ScrapingDog Profile API
    Handles async (202) responses with retries
    """

    linkedin_id = extract_linkedin_id(linkedin_url)

    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "id": linkedin_id,
        "type": "profile",
        "premium": "true" if premium else "false",
        "webhook": "false",
        "fresh": "false",
    }

    for attempt in range(1, retries + 1):
        response = requests.get(
            SCRAPINGDOG_PROFILE_ENDPOINT,
            params=params,
            timeout=30
        )

        # Job queued
        if response.status_code == 202:
            print(
                f"[LinkedIn] Job queued (attempt {attempt}/{retries}). "
                f"Retrying in {wait_seconds}s..."
            )
            time.sleep(wait_seconds)
            continue

        # Success
        if response.status_code == 200:
            data = safe_json(response)
            if data:
                return data
            return None

        # Other error
        print(f"[LinkedIn] Request failed: {response.status_code}")
        print(response.text[:500])
        return None

    print("[LinkedIn] Max retries exceeded.")
    return None


def parse_linkedin_profile(raw_data):
    if not raw_data or not isinstance(raw_data, list):
        return {}

    data = raw_data[0]  # ScrapingDog returns a list of profiles, we only want our one
    profile = {}

    # Basic info
    profile["full_name"] = data.get("fullName")
    profile["first_name"] = data.get("first_name")
    profile["last_name"] = data.get("last_name")
    profile["headline"] = data.get("headline")
    profile["location"] = data.get("location")
    profile["followers"] = data.get("followers")
    profile["connections"] = data.get("connections")
    profile["about"] = data.get("about")
    profile["profile_photo"] = data.get("profile_photo")
    profile["background_image"] = data.get("background_cover_image_url")

    # Experience
    profile["experience"] = []
    for exp in data.get("experience", []):
        profile["experience"].append({
            "company_name": exp.get("company_name"),
            "company_image": exp.get("company_image"),
            "position": exp.get("position"),
            "start_date": exp.get("starts_at"),
            "end_date": exp.get("ends_at"),
        })

    # Education
    profile["education"] = []
    for edu in data.get("education", []):
        profile["education"].append({
            "school_name": edu.get("school_name"),
            "degree": edu.get("degree"),
            "start_date": edu.get("starts_at"),
            "end_date": edu.get("ends_at"),
        })

    # Volunteering
    profile["volunteering"] = []
    for vol in data.get("volunteering", []):
        profile["volunteering"].append({
            "position": vol.get("company_position"),
            "organization": vol.get("company_name"),
            "start_date": vol.get("starts_at"),
            "end_date": vol.get("ends_at"),
            "url": vol.get("company_url"),
        })

    # Projects
    profile["projects"] = []
    for proj in data.get("projects", []):
        profile["projects"].append({
            "title": proj.get("title"),
            "link": proj.get("link"),
            "duration": proj.get("duration")
        })

    # Certifications
    profile["certifications"] = []
    for cert in data.get("certification", []):
        profile["certifications"].append({
            "title": cert.get("certification"),
            "issuer": cert.get("company_name"),
            "issue_date": cert.get("issue_date"),
            "credential_url": cert.get("credential_url")
        })

    # Languages
    profile["languages"] = []
    for lang in data.get("languages", []):
        profile["languages"].append({
            "name": lang.get("name"),
            "level": lang.get("level")
        })

    # Activities
    profile["activities"] = []
    for act in data.get("activities", []):
        profile["activities"].append({
            "title": act.get("title"),
            "link": act.get("link"),
            "activity_type": act.get("activity")
        })

    return profile



# ----------------------------------
# Pretty Printing (nested-safe)
# ----------------------------------

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


# ----------------------------------
# CLI test
# ----------------------------------

if __name__ == "__main__":
    test_url = "https://www.linkedin.com/in/rayan-akhtar/"

    # Step 1: Scrape raw data from ScrapingDog
    raw_profile_data = linkedin_person_scrape(test_url)

    if raw_profile_data:
        # Step 2: Parse/normalize the profile
        profile = parse_linkedin_profile(raw_profile_data)

        # Step 3: Pretty print the cleaned profile
        print("\n=== LINKEDIN PROFILE DATA (PARSED) ===\n")
        pretty_print(profile)
    else:
        print("No LinkedIn data returned or scraping failed.")
