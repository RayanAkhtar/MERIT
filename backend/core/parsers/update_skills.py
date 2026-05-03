import json
import urllib.request
import os

# pulls the latest skills from the devicon dataset to keep our matching list fresh.
# source is https://github.com/devicons/devicon

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

    # manual additions for stuff the devicon dataset misses or names differently
    # this is key so the semantic matcher has these in the candidate skill set
    languages.update(["SQL", "PostgreSQL", "MySQL", "SQLite", "NoSQL", "Python", "Java", "C++", "JavaScript", "TypeScript"])
    frameworks.update(["React", "Node.js", "Express", "Django", "Flask", "AWS", "Docker", "Kubernetes", "Next.js", "Supabase"])

    output = {
        "languages": sorted(list(languages)),
        "frameworks": sorted(list(frameworks))
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Successfully updated skills_data.json at {OUTPUT_FILE}")

if __name__ == "__main__":
    update_skills()
