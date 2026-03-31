import json
import urllib.request
import os

# This script updates the skills database using the official Devicon dataset.
#     Source:  Devicon (https://github.com/devicons/devicon)
#     License: MIT License
#     Purpose: To provide a standardised and comprehensive list of programming 
#              languages and frameworks for the job description parser.

DEVICON_URL = "https://raw.githubusercontent.com/devicons/devicon/master/devicon.json"

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "skills_data.json")

def update_skills():
    print(f"Fetching skills data from {DEVICON_URL}...")
    try:
        with urllib.request.urlopen(DEVICON_URL) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    languages = set()
    frameworks = set()

    for item in data:
        name = item.get("name", "")
        tags = item.get("tags", [])
        altnames = item.get("altnames", [])
        
        # categorising based on type
        is_lang = "language" in tags or "programming" in tags
        is_framework = "framework" in tags or "library" in tags or "database" in tags or "cloud" in tags

        if is_lang:
            languages.add(name)
            for alt in altnames:
                if len(alt) > 1: languages.add(alt.capitalize() if len(alt) > 3 else alt.upper())
        
        if is_framework:
            frameworks.add(name)
            for alt in altnames:
                if len(alt) > 1: frameworks.add(alt.capitalize() if len(alt) > 3 else alt.upper())


    output = {
        "languages": sorted(list(languages)),
        "frameworks": sorted(list(frameworks))
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Successfully updated skills_data.json at {OUTPUT_FILE}")

if __name__ == "__main__":
    update_skills()
