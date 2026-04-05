import os
import requests
from typing import Dict, Optional

# Legacy/unused code

# Keeping this slightly redundant file here, just incase Apify fails in the future
# Or if apify starts charging more 

SCRAPINGDOG_API_KEY = os.getenv("SCRAPINGDOG_API_KEY")
SCRAPINGDOG_PROFILE_ENDPOINT = "https://api.scrapingdog.com/profile"

def scrapingdog_person_scrape(linkedin_url: str) -> Optional[Dict]:
    """Legacy ScrapingDog scraper."""
    if not SCRAPINGDOG_API_KEY:
        return None
        
    print(f"[LinkedIn] Attempting Fallback Scrape via ScrapingDog for: {linkedin_url}")
    params = {
        "api_key": SCRAPINGDOG_API_KEY,
        "link": linkedin_url
    }
    try:
        response = requests.get(SCRAPINGDOG_PROFILE_ENDPOINT, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[LinkedIn] ScrapingDog exception: {str(e)}")
    return None

def parse_scrapingdog_profile(data):
    """Legacy ScrapingDog normalization logic."""
    profile = {}
    profile["full_name"] = data.get("fullName") or f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
    profile["first_name"] = data.get("first_name")
    profile["last_name"] = data.get("last_name")
    profile["headline"] = data.get("headline")
    profile["location"] = data.get("location")
    profile["followers"] = data.get("followers")
    profile["connections"] = data.get("connections")
    profile["about"] = data.get("about")
    profile["profile_photo"] = data.get("profile_photo")
    profile["background_image"] = data.get("background_cover_image_url")

    profile["experience"] = []
    for exp in (data.get("experience") or []):
        profile["experience"].append({
            "company_name": exp.get("company_name"),
            "position": exp.get("position"),
            "start_date": exp.get("starts_at"),
            "end_date": exp.get("ends_at"),
            "description": exp.get("description")
        })

    profile["education"] = []
    for edu in (data.get("education") or []):
        profile["education"].append({
            "school_name": edu.get("school_name"),
            "degree": edu.get("degree"),
            "start_date": edu.get("starts_at"),
            "end_date": edu.get("ends_at")
        })

    profile["projects"] = []
    for proj in (data.get("projects") or []):
        profile["projects"].append({
            "title": proj.get("title"),
            "link": proj.get("link"),
            "duration": proj.get("duration"),
            "description": proj.get("description")
        })

    return profile
