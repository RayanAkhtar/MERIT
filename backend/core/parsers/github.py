import os
import re
import requests
from collections import Counter
from pprint import pprint

# Todo later:
#   1. Update skills to be taken from the job description itself
#   2. Update experience parsing to parse as a list of structured experience
#   3. Update education parsing to parse as list of structured education
#   4. Check robustness of link extraction, embedded links, non embedded links, usernames, etc
#   5. Check against different CV formats



# Current structure of `profile` returned by parse_github_user:
# {
#     "username": str,
#     "name": str | None,
#     "bio": str | None,
#     "company": str | None,
#     "location": str | None,
#     "email": str | None,
#     "blog": str | None,
#     "twitter": str | None,
#     "avatar_url": str (URL),
#     "profile_url": str (URL),
#     "created_at": str (ISO timestamp),
#     "followers": int,
#     "following": int,
#     "public_repos": int,
#     "repositories": [        # list of dicts, one per repo
#         {
#             "name": str,
#             "description": str | None,
#             "language": str | None,
#             "topics": list[str],
#             "stars": int,
#             "forks": int,
#             "license": str | None,
#             "is_fork": bool,
#             "updated_at": str (ISO timestamp),
#             "url": str (repo URL)
#         },
#         ...
#     ],
#     "repository_summary": {  # aggregated info across repos
#         "repo_count": int,
#         "top_languages": dict[str, int],  # language name -> count
#         "total_stars": int,
#         "total_forks": int,
#         "most_starred_repos": [         # list of top 5 repos by stars
#             {
#                 "name": str,
#                 "stars": int,
#                 "url": str
#             },
#             ...
#         ]
#     }
# }




# ----------------------------
# Configuration
# ----------------------------

GITHUB_API_BASE = "https://api.github.com"

GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json"
}


# ----------------------------
# Utilities
# ----------------------------

def extract_github_username(url: str) -> str | None:
    """
    Extracts username from:
    - https://github.com/username
    - https://github.com/username/
    """
    match = re.match(r"https?://(www\.)?github\.com/([^/]+)", url)
    return match.group(2) if match else None


def github_get(endpoint: str, params=None):
    response = requests.get(
        f"{GITHUB_API_BASE}{endpoint}",
        headers=GITHUB_HEADERS,
        params=params
    )
    response.raise_for_status()
    return response.json()


# ----------------------------
# Core Parsing Logic
# ----------------------------

def fetch_user_profile(username: str) -> dict:
    return github_get(f"/users/{username}")


def fetch_user_repos(username: str) -> list[dict]:
    repos = []
    page = 1

    while True:
        batch = github_get(
            f"/users/{username}/repos",
            params={
                "per_page": 100,
                "page": page,
                "sort": "updated"
            }
        )

        if not batch:
            break

        repos.extend(batch)
        page += 1

    return repos


def summarize_repositories(repos: list[dict]) -> dict:
    languages = Counter()
    total_stars = 0
    total_forks = 0

    for repo in repos:
        if repo.get("language"):
            languages[repo["language"]] += 1
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)

    most_starred = sorted(
        repos,
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True
    )[:5]

    return {
        "repo_count": len(repos),
        "top_languages": dict(languages.most_common(10)),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "most_starred_repos": [
            {
                "name": r["name"],
                "stars": r["stargazers_count"],
                "url": r["html_url"]
            }
            for r in most_starred
        ]
    }


def parse_github_user(url: str) -> dict:
    username = extract_github_username(url)
    if not username:
        raise ValueError(f"Invalid GitHub URL: {url}")

    profile = fetch_user_profile(username)
    repos = fetch_user_repos(username)

    repo_summary = summarize_repositories(repos)

    return {
        "username": profile["login"],
        "name": profile.get("name"),
        "bio": profile.get("bio"),
        "company": profile.get("company"),
        "location": profile.get("location"),
        "email": profile.get("email"),
        "blog": profile.get("blog"),
        "twitter": profile.get("twitter_username"),
        "avatar_url": profile.get("avatar_url"),
        "profile_url": profile.get("html_url"),
        "created_at": profile.get("created_at"),
        "followers": profile.get("followers"),
        "following": profile.get("following"),
        "public_repos": profile.get("public_repos"),
        "repositories": [
            {
                "name": r["name"],
                "description": r.get("description"),
                "language": r.get("language"),
                "topics": r.get("topics", []),
                "stars": r.get("stargazers_count"),
                "forks": r.get("forks_count"),
                "license": r["license"]["name"] if r.get("license") else None,
                "is_fork": r.get("fork"),
                "updated_at": r.get("updated_at"),
                "url": r.get("html_url"),
            }
            for r in repos
        ],
        "repository_summary": repo_summary
    }


if __name__ == "__main__":
    test_url = "https://github.com/RayanAkhtar"
    data = parse_github_user(test_url)

    pprint(data, sort_dicts=False)