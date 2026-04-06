import os
import re
import requests
import datetime
from collections import Counter
from collections import defaultdict
from core.parsers.base import BaseDataSource

GITHUB_API_BASE = "https://api.github.com"
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json"
}

# avoid rate limit by using github tokens
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if GITHUB_TOKEN:
    GITHUB_HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# utilities

def extract_github_username(url: str) -> str | None:
    match = re.match(r"https?://(www\.)?github\.com/([^/]+)", url)
    return match.group(2) if match else None


def github_get(endpoint: str, params=None, headers=None):
    request_headers = GITHUB_HEADERS.copy()
    if headers:
        request_headers.update(headers)
        
    response = requests.get(
        f"{GITHUB_API_BASE}{endpoint}",
        headers=request_headers,
        params=params
    )
        
    response.raise_for_status()
    return response.json()


# core parsing logic

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


def fetch_repo_languages(repo_full_name: str) -> dict:
    return github_get(f"/repos/{repo_full_name}/languages")


def fetch_user_contribution_ratio(repo_full_name: str, username: str) -> float:
    stats = github_get(f"/repos/{repo_full_name}/stats/contributors")
    
    # assuming that the repo is theirs if there are issues
    if not stats or not isinstance(stats, list):
        return 1.0
        
    user_stats = next((s for s in stats if s.get("author", {}).get("login") == username), None)
    # if no stats found, assume they didnt contribute to that repo
    if not user_stats:
        return 0.0
        
    user_additions = sum(w.get("a", 0) for w in user_stats.get("weeks", []))
    total_additions = sum(sum(w.get("a", 0) for w in s.get("weeks", [])) for s in stats)
    if total_additions <= 0:
        return 1.0
        
    return min(user_additions / total_additions, 1.0)


def fetch_user_activity(username: str) -> dict:
    # pull requests that were authorised by the user
    pr_search = github_get("/search/issues", params={"q": f"author:{username} type:pr"})
    total_prs = pr_search.get("total_count", 0)
    
    # commits authorised by the user
    commit_search = github_get(
        "/search/commits", 
        params={"q": f"author:{username}"}, 
        headers={"Accept": "application/vnd.github.cloak-preview+json"}
    )
    total_commits = commit_search.get("total_count", 0)
    
    # open source contributions, PRs to repos not owned by the user
    oss_search = github_get("/search/issues", params={
        "q": f"is:pr author:{username} -user:{username}",
        "per_page": 100
    })
    oss_prs = oss_search.get("total_count", 0)
    oss_repos = {item.get("repository_url") for item in oss_search.get("items", []) if item.get("repository_url")}
    external_repos_count = len(oss_repos)
    
    return {
        "total_prs": total_prs,
        "total_commits": total_commits,
        "oss_prs": oss_prs,
        "external_repos": external_repos_count
    }


def summarise_repositories(repos: list[dict], username: str) -> dict:
    # Assume 80 chars per line (PEP 8 standard) to guess LOC from bytes
    # ref: https://peps.python.org/pep-0008/#maximum-line-length
    CHARS_PER_LINE = 80

    total_languages = Counter()
    total_stars = 0
    total_forks = 0
    total_bytes = 0
    
    language_history = defaultdict(lambda: Counter())

    # excluding forks, we only want original repos that the user themselve have created
    original_repos = [r for r in repos if not r.get("fork")]

    # fetch language bytes for each original repo for deep analysis
    for i, repo in enumerate(original_repos):
        repo_langs = {}
        # the ratio of the code the user actually wrote
        ratio = 1.0
        
        # avoid excessive scanning, or rate limit, by only checking 15 repos per user
        REPO_LIMIT = 15
        if i < REPO_LIMIT:
            repo_langs = fetch_repo_languages(repo["full_name"])

            # only perform ratio check if we have languages and it might be a team project
            if repo_langs and repo.get("stargazers_count", 0) > 0:
                ratio = fetch_user_contribution_ratio(repo["full_name"], username)
            
        if repo_langs:
            # github doesnt show language use per year
            # so we just spread it across the year range instead
            start_year = int(repo.get("created_at", "2000")[:4])
            end_year = int(repo.get("updated_at", str(datetime.datetime.now().year))[:4])
            active_years_count = max(1, end_year - start_year + 1)
            
            for lang, byte_count in repo_langs.items():
                personal_total = int(byte_count * ratio)
                total_languages[lang] += personal_total
                total_bytes += personal_total
                
                # distribute lines across active years for that repo
                per_year_bytes = personal_total // active_years_count
                for yr_int in range(start_year, end_year + 1):
                    yr_str = str(yr_int)
                    language_history[yr_str][lang] += per_year_bytes
            
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)

    # top 3 repos to show on the frontend as a highlight (when in extract/cvs)
    most_starred = sorted(
        original_repos,
        key=lambda r: r.get("stargazers_count", 0),
        reverse=True
    )[:3]

    featured_repos = []
    for r in most_starred:
        r_langs = fetch_repo_languages(r["full_name"])
        top_5_langs = sorted(r_langs.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 'type' based on topics
        topics = r.get("topics", [])
        proj_type = topics[0].title() if topics else "Original Project"
        
        featured_repos.append({
            "name": r["name"],
            "type": proj_type,
            "stars": r["stargazers_count"],
            "description": r.get("description") or "No description provided.",
            "url": r["html_url"],
            "top_languages": [l[0] for l in top_5_langs]
        })

    # top 12 languages
    sorted_langs = sorted(total_languages.items(), key=lambda x: x[1], reverse=True)
    top_12 = []
    for lang, byte_count in sorted_langs[:12]:
        percentage = round((byte_count / total_bytes) * 100, 1) if total_bytes > 0 else 0
        top_12.append({
            "label": lang,
            "pct": percentage
        })

    # top 12 langauges in top 15 repos
    top_15_overall = [l[0] for l in sorted_langs[:REPO_LIMIT]]
    formatted_history = []
    
    current_year = str(datetime.datetime.now().year)
    all_years = sorted(list(language_history.keys()))
    if all_years and current_year not in all_years:
        all_years.append(current_year)
    
    for yr in all_years:
        year_entry = {"year": yr}
        for lang in top_15_overall:
            year_entry[lang] = language_history[yr][lang] // CHARS_PER_LINE
        formatted_history.append(year_entry)

    return {
        "repo_count": len(original_repos),
        "total_lines": total_bytes // CHARS_PER_LINE,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "languages": top_12,
        "featured_projects": featured_repos,
        "language_history": formatted_history
    }


class GitHubDataSource(BaseDataSource):
    @property
    def name(self) -> str:
        return "github"

    def validate_url(self, url: str) -> bool:
        return extract_github_username(url) is not None

    def scrape(self, url: str) -> dict:
        username = extract_github_username(url)
        if not username:
            raise ValueError(f"Invalid GitHub URL: {url}")
            
        profile = fetch_user_profile(username)
        repos = fetch_user_repos(username)
        activity = fetch_user_activity(profile.get("login", username))
        
        return {
            "profile": profile,
            "repos": repos,
            "activity": activity,
            "url": url
        }

    def parse(self, raw_data: dict) -> dict:
        profile = raw_data["profile"]
        repos = raw_data["repos"]
        activity = raw_data["activity"]
        username = profile.get("login", "")
        
        repo_summary = summarise_repositories(repos, username)
        
        return {
            "source": self.name,
            "username": username,
            "name": profile.get("name"),
            "bio": profile.get("bio"),
            "company": profile.get("company"),
            "location": profile.get("location"),
            "email": profile.get("email"),
            "avatar_url": profile.get("avatar_url"),
            "profile_url": profile.get("html_url") or raw_data["url"],
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
            **activity,
            **repo_summary
        }
