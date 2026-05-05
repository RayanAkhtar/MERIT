from typing import Dict, Any, List
import math
from .base import BaseMetric
from .semantic_utils import semantic_matcher
from .constants import SCORING_CONSTANTS
from core.fusion.bayesian import BayesianEvidenceFusion, Evidence

class ExperienceMetric(BaseMetric):
    def _fuse_evidence(self, evidence: List[Evidence]) -> Dict[str, Any]:
        fusion = BayesianEvidenceFusion(
            prior_alpha=SCORING_CONSTANTS["FUSION"]["PRIORS"]["ALPHA"],
            prior_beta=SCORING_CONSTANTS["FUSION"]["PRIORS"]["BETA"],
            high_threshold=SCORING_CONSTANTS["FUSION"]["THRESHOLDS"]["HIGH"],
            medium_threshold=SCORING_CONSTANTS["FUSION"]["THRESHOLDS"]["MEDIUM"]
        )
        return fusion.fuse(evidence)

    @property
    def id(self) -> str:
        return "experience"
    
    @property
    def name(self) -> str:
        return "Professional Experience Over Time"
        
    @property
    def description(self) -> str:
        return "Evaluates career trajectory, role progression, and years of applicable experience across CV and LinkedIn."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        from datetime import datetime
        import re

        def parse_to_months(date_str):
            if not date_str or not isinstance(date_str, str): return None
            date_str = date_str.lower().strip()
            if 'present' in date_str or 'current' in date_str:
                return datetime.now().year * 12 + datetime.now().month
            
            # Handle ISO YYYY-MM-DD
            iso_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
            if iso_match:
                return int(iso_match.group(1)) * 12 + int(iso_match.group(2))

            # Match "MMM YYYY" or "YYYY"
            match = re.search(r'(\w+)?\s*(\d{4})', date_str)
            if not match: return None
            
            month_map = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}
            month_part = match.group(1)[:3] if match.group(1) else 'jan'
            month = month_map.get(month_part, 1)
            year = int(match.group(2))
            return year * 12 + month

        # work out the tenure for each source separately
        cv_exp_data = candidate_data.get('cv_experience', []) or []
        
        # if the structured list is empty, try to parse the raw text instead
        if not cv_exp_data and candidate_data.get('experience'):
            raw_text = candidate_data.get('experience', '')
            if isinstance(raw_text, str):
                lines = raw_text.split('\n')
                cv_exp = []
                for line in lines:
                    # Look for things like "2020 - 2023" or "2021 to Present"
                    range_match = re.search(r'(\d{4})\s*[\-\u2013\u2014\w]+\s*(\d{4}|Present|Current)', line, re.IGNORECASE)
                    if range_match:
                        cv_exp.append({"start_date": range_match.group(1), "end_date": range_match.group(2)})
            elif isinstance(raw_text, list):
                cv_exp = raw_text
            else:
                cv_exp = []
        else:
            cv_exp = cv_exp_data if isinstance(cv_exp_data, list) else []

        li_exp = candidate_data.get('linkedin_experience', []) or candidate_data.get('linkedin_history', [])
        
        cv_months = 0
        for e in cv_exp:
            if not isinstance(e, dict): continue
            s, en = parse_to_months(e.get('start_date')), parse_to_months(e.get('end_date'))
            if s and en: 
                cv_months += max(0, en - s)
            else:
                dur = e.get('duration_months') or e.get('duration') or e.get('months') or (e.get('years', 0) * 12)
                if isinstance(dur, (int, float)): cv_months += int(dur)
        
        li_months = 0
        for e in li_exp:
            if not isinstance(e, dict): continue
            s, en = parse_to_months(e.get('start_date')), parse_to_months(e.get('end_date'))
            if s and en: li_months += max(0, en - s)
            else:
                dur = e.get('duration_months') or e.get('duration') or e.get('months', 0)
                if isinstance(dur, (int, float)): li_months += int(dur)

        # use the longest timeline as the main tenure
        total_months = max(cv_months, li_months)
        sources_used = list(set(["CV"] + (["LinkedIn"] if li_months > 0 else [])))

        # target for normalisation (per source to avoid one source clouding the other)
        batch_max = candidate_data.get('batch_max_tenure', 60)
        cv_target = max(candidate_data.get('batch_max_cv_tenure', batch_max), 12)
        li_target = max(candidate_data.get('batch_max_li_tenure', batch_max), 12)
        
        cv_tenure_score = min(1.0, cv_months / cv_target)
        li_tenure_score = min(1.0, li_months / li_target)
        
        # for overall metrics, use the higher of the two normalised scores
        tenure_score = max(cv_tenure_score, li_tenure_score)
        
        # check on description density, longer usually means better quality
        all_summaries = " ".join([e.get("summary", "") for e in cv_exp if isinstance(e, dict)])
        primary_summary = str(candidate_data.get('experience_summary') or '')
        li_about = str((candidate_data.get('linkedin_profile', {}) or {}).get('about') or '')
        
        combined_density_text = f"{all_summaries} {primary_summary} {li_about}".strip()
        text_length = len(combined_density_text)
        
        # base score for having roles, then scale it by how much theyve written
        quality_proxy = 0.0
        if text_length > 0 or len(cv_exp) > 0 or len(li_exp) > 0:
            quality_proxy = min(1.0, 0.2 + (text_length / 4000.0))
        
        # Probabilistic Evidence Aggregation
        # Bayesian fusion handles discrepancies between CV and LinkedIn dates
        evidence = []
        conf = SCORING_CONSTANTS["FUSION"]["SOURCE_CONFIDENCE"]["PROFESSIONAL_HISTORY"]
        
        # CV Signal
        if cv_months > 0:
            evidence.append(Evidence(source="CV", confidence=conf["CV"], strength=cv_tenure_score))
        
        # LI Signal
        if li_months > 0:
            evidence.append(Evidence(source="LinkedIn", confidence=conf["LINKEDIN"], strength=li_tenure_score))
            
        fusion_result = self._fuse_evidence(evidence)
        tenure_component_score = fusion_result["fused_score"]
        conf_label = fusion_result["confidence_label"]
        
        # Combine the tenure (85%) and the quality proxy (15%) for the final metric
        final_score = (tenure_component_score * 0.85) + (quality_proxy * 0.15)
        
        # Recruiter notes: keep it simple
        human_note = "Professional history verified across multiple sources." if conf_label == "High Confidence" else "Variation detected in career timelines across sources."
        if not evidence: human_note = "No verifiable professional history found."
        
        # Work out the gap for the improvements section
        tenure_gap = max(0, cv_target - cv_months) 
        tenure_note = "Maximum tenure achieved for this batch benchmark." if tenure_score >= 1.0 else f"Current tenure is {tenure_gap} months below the batch peak of {cv_target} months."
        
        density_note = "Highly detailed career narrative provided." if quality_proxy >= 0.8 else "Consider providing more detail for your roles to improve evidence depth."

        return {
            "score": round(final_score, 2),
            "raw_months": total_months,
            "raw_cv_months": cv_months,
            "raw_li_months": li_months,
            "calculation_formula": "(FusedTenure * 0.85) + (NarrativeDepth * 0.15)",
            "technical_formula": f"(Fused_Tenure({tenure_component_score:.2f}) * 0.85) + (Narrative_Depth({quality_proxy:.2f}) * 0.15) = {final_score:.2f}",
            "breakdown": [
                {
                    "component": "Career Timeline Breadth",
                    "score": round(tenure_component_score, 2),
                    "weight": 0.85,
                    "notes": f"{human_note} (Bayesian Audit: {fusion_result.get('logic', 'N/A')})",
                    "alpha": fusion_result.get("alpha"),
                    "beta": fusion_result.get("beta"),
                    "source_details": [
                        {
                            "source": "CV", 
                            "score": cv_tenure_score, 
                            "trust": conf["CV"],
                            "derivation": f"min(1.0, {cv_months}m / {cv_target}m)",
                            "explanation": f"Professional history extracted from CV: {cv_months} months."
                        },
                        {
                            "source": "LinkedIn", 
                            "score": li_tenure_score, 
                            "trust": conf["LINKEDIN"],
                            "derivation": f"min(1.0, {li_months}m / {li_target}m)",
                            "explanation": f"Professional history validated by LinkedIn: {li_months} months."
                        }
                    ]
                },
                {
                    "component": "Contribution Narrative Depth",
                    "score": round(quality_proxy, 2),
                    "weight": 0.15,
                    "notes": density_note,
                    "source_details": [
                        {"source": "CV", "score": round(quality_proxy, 2), "explanation": f"Detail level based on {text_length} characters of role descriptions."},
                        {"source": "LinkedIn", "score": round(quality_proxy, 2), "explanation": f"Supplemental depth from LinkedIn 'About' section."}
                    ]
                }
            ],
            "sources_used": list(set(sources_used)),
            "glossary": [],
            "improvements": [i for i in [
                {"text": f"Add {tenure_gap} more months of relevant history to your CV to match the top candidate.", "gain": 0.85 * (1.0 - tenure_component_score)} if tenure_component_score < 0.9 else None,
                {"text": "Elaborate on your specific responsibilities in your most recent roles to improve Narrative Depth.", "gain": 0.15 * (1.0 - quality_proxy)} if quality_proxy < 0.9 else None
            ] if i is not None]
        }

class ProjectsMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "projects"
    
    @property
    def name(self) -> str:
        return "Technical Projects & Contributions"
        
    @property
    def description(self) -> str:
        return "Assesses the scale, impact, and relevance of public and documented technical projects."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        from difflib import SequenceMatcher
        import math
        
        def is_similar(cv_title, gh_name):
            # Lenient keyword matching
            cv_words = set(cv_title.lower().replace('-', ' ').replace('_', ' ').split())
            gh_words = set(gh_name.lower().replace('-', ' ').replace('_', ' ').split())
            common = cv_words.intersection(gh_words)
            # If they share a technical word > 3 chars, it's a match
            if any(len(w) > 3 and w not in ['project', 'task', 'code', 'app', 'main'] for w in common): return True
            return SequenceMatcher(None, cv_title.lower(), gh_name.lower()).ratio() > 0.5

        # get projects from everywhere we can
        cv_raw = candidate_data.get('projects_history', []) or []
        if not cv_raw: cv_raw = [{"title": p} if isinstance(p, str) else p for p in (candidate_data.get('projects', []) or [])]
        
        github_data = candidate_data.get('github_enriched', {}) or {}
        gh_raw = github_data.get('featured_projects', []) or github_data.get('repositories', []) or []
        
        # match up cv entries with github repos to find private stuff
        verifications = []
        private_projects = []
        for cv_p in cv_raw:
            title = str(cv_p.get('title') or cv_p.get('name') or "")
            if not title: continue
            
            matched = False
            for gh_p in gh_raw:
                gh_n = str(gh_p.get('name', ""))
                if is_similar(title, gh_n):
                    verifications.append(title)
                    matched = True
                    break
            if not matched:
                private_projects.append(title)

        # github traction (how popular their stuff is)
        repo_count = (github_data.get('repo_count') or 0) or len(gh_raw)
        stars = github_data.get('total_stars') or 0
        forks = github_data.get('total_forks') or 0
        
        # Raw Traction = (Repos * 0.05) + log10(Stars+Forks+1) * 0.15
        # use raw points for the batch-wide scaling
        gh_base = repo_count * 0.05
        gh_impact = math.log10(stars + forks + 1) * 0.15
        raw_traction = gh_base + gh_impact
        
        # Relative Traction Scaling
        batch_max_traction = candidate_data.get('batch_max_traction', 0.7) # Default to 0.7 if no batch context
        traction_score = min(0.7, raw_traction / batch_max_traction * 0.7) if batch_max_traction > 0 else 0.0
        
        # cv and verification logic
        # Verified projects are worth more than private ones
        cv_points = min(0.3, (len(verifications) * 0.08) + (len(private_projects) * 0.04))
        verification_bonus = len(verifications) * 0.10

        final_score = min(1.0, traction_score + cv_points + verification_bonus)
        
        return {
            "score": round(final_score, 2),
            "raw_traction_points": raw_traction, # Consumed by ranking engine for batch context
            "breakdown": [
                {
                    "component": "Technical Portfolio & Traction",
                    "score": round(final_score, 2),
                    "recalculation_strategy": "sum",
                    "notes": f"Portfolio Score driven by {repo_count} repos ({stars}★) relative to batch peak traction of {batch_max_traction:.2f}.",
                    "source_details": [
                        {
                            "source": "GitHub", 
                            "score": round(traction_score, 2), 
                            "explanation": f"Traction: ({repo_count} repos * 0.05) + (log10({stars+forks+1}) * 0.15) = {raw_traction:.2f} pts / BatchPeak {batch_max_traction:.2f} * 0.7 limit = {traction_score:.2f}"
                        },
                        {
                            "source": "CV", 
                            "score": round(cv_points, 2), 
                            "explanation": f"Portfolio: ({len(verifications)} verified * 0.08) + ({len(private_projects)} private * 0.04) = {cv_points:.2f}. Internal: {', '.join(private_projects[:3])}{'...' if len(private_projects) > 3 else ''}"
                        },
                        {
                            "source": "Verification Bonus", 
                            "score": round(verification_bonus, 2), 
                            "explanation": f"Granting +10% bonus for {len(verifications)} Elastic Matches (CV ↔ GitHub)."
                        }
                    ]
                }
            ],
            "sources_used": ["CV", "GitHub"],
            "calculation_formula": "(RelativeTraction / BatchMax) + Volume(CV) + VerificationBonus",
            "technical_formula": f"{traction_score:.2f} (Traction) + {cv_points:.2f} (Portfolio) + {verification_bonus:.2f} (Verification) = {final_score:.2f}",
            "glossary": [
                {
                    "variable": "Traction(GH)",
                    "description": "How much people actually use or star their repos on GitHub.",
                    "impact": "Primary driver for engineering visibility.",
                    "sensitivity": "Sensitive to high-star individual repositories."
                },
                {
                    "variable": "Volume(CV)",
                    "description": "How many projects they've listed, with a bonus if we can verify them on GitHub.",
                    "impact": "Ensures academic and institutional work is credited.",
                    "sensitivity": "Private projects count for about half of what a verified one does."
                },
                {
                    "variable": "VerificationBonus",
                    "description": "A nice little boost if we find the same project on both their CV and GitHub.",
                    "impact": "High-confidence verification signal.",
                    "sensitivity": "Uses 'Elastic Matching' to find project name overlaps."
                }
            ],
            "improvements": [
                {
                    "text": f"The batch peaks for this metric are {candidate_data.get('batch_max_repos', 0)} repositories and {candidate_data.get('batch_max_stars', 0)} stars. To match the leaders, increase your public code visibility.",
                    "gain": 0.1
                },
                {
                    "text": "Link your private work projects on your CV to your GitHub to ensure they are verified for full credit.",
                    "gain": 0.05
                }
            ]
        }

class TechSkillsMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "techSkills"
    
    @property
    def name(self) -> str:
        return "Technical Skills & Tooling Depth"
        
    @property
    def description(self) -> str:
        return "Evaluates the breadth and practical depth of the candidate's engineering toolbelt."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        # Aggregate all unique skills from the candidate's profile
        raw_skills = candidate_data.get('skills', []) or []
        candidate_skills = sorted(list(set([s.lower() for s in raw_skills])))
        skill_count = len(candidate_skills)
        
        # Simple Categorisation Logic
        categories = {
            "Languages": ["python", "javascript", "typescript", "java", "c++", "c#", "ruby", "go", "rust", "php", "swift", "kotlin", "sql", "html", "css"],
            "Frameworks & Libs": ["react", "angular", "vue", "django", "flask", "fastapi", "spring", "express", "next.js", "pytorch", "tensorflow", "keras", "scikit-learn", "numpy", "pandas"],
            "Infra & Cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "github actions", "postgresql", "mongodb", "redis", "mysql", "linux", "nginx"],
            "Tools & Other": ["git", "jira", "figma", "postman", "unity", "unreal", "graphql", "rest", "grpc", "node.js"]
        }
        
        categorised = {cat: [] for cat in categories}
        uncategorised = []
        for skill in candidate_skills:
            found = False
            for cat, keywords in categories.items():
                if any(k in skill for k in keywords):
                    categorised[cat].append(skill.capitalize())
                    found = True
                    break
            if not found:
                uncategorised.append(skill.capitalize())
        
        if uncategorised:
            categorised["General Tech"] = uncategorised
            
        # Batch Relative Scaling
        batch_max = candidate_data.get('batch_max_skill_count', 10)
        score = min(1.0, skill_count / batch_max) if batch_max > 0 else 0.0
        
        # stuff for the UI audit
        source_details = [
            {
                "name": "Aggregate Breadth",
                "source": "Toolbelt Signal",
                "score": round(score, 2),
                "explanation": f"Total volume: {skill_count} unique technologies."
            }
        ]
        for cat, items in categorised.items():
            if items:
                source_details.append({
                    "name": cat,
                    "source": f"Technical Detail: {cat}",
                    "score": 1.0,
                    "explanation": f"Detected {len(items)} items: {', '.join(items[:8])}{'...' if len(items) > 8 else ''}"
                })

        return {
            "score": round(score, 2),
            "breakdown": [
                {
                    "component": "Technical Breadth & Toolbelt Depth",
                    "score": round(score, 2),
                    "notes": f"Detected {skill_count} unique technologies across {len(source_details)} functional categories.",
                    "source_details": [s for s in source_details if "Signal" in s["source"]] + [s for s in source_details if "Detail" in s["source"]]
                }
            ],
            "sources_used": ["CV", "GitHub", "LinkedIn"],
            "calculation_formula": "Unique_Skills / Batch_Max_Skills",
            "technical_formula": f"{skill_count} Skills / {batch_max} Peak = {score:.2f}",
            "glossary": [
                {
                    "variable": "Technical Breadth",
                    "description": "Total volume of unique technologies detected across all professional signals.",
                    "impact": "Indicates generalist versatility and engineering adaptability.",
                    "sensitivity": "Rewards candidates with diverse project exposure."
                }
            ],
            "improvements": [
                {
                    "text": f"The most versatile candidate in this batch knows {batch_max} technologies. Highlighting more specific frameworks and tools from your history can close this gap.",
                    "gain": round(1.0 - score, 2)
                }
            ]
        }

class GithubComplexityMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "intel_github_complexity"
    
    @property
    def name(self) -> str:
        return "Project Complexity & Architecture"
        
    @property
    def description(self) -> str:
        return "Analyses the architectural complexity and lines of code of open source contributions."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        gh_data = candidate_data.get('github_enriched', {})
        # use the full repo list for the depth analysis
        projects = gh_data.get('repositories', []) or gh_data.get('featured_projects', [])
        
        if not gh_data and not projects:
            return {"score": 0.0, "raw_complexity_sum": 0.0, "breakdown": [], "sources_used": ["GitHub"], "formula": "none", "technical_formula": "none", "glossary": [], "improvements": [{"text": "No GitHub data available", "gain": 0.0}]}
            
        project_complexities = []
        source_details = []
        
        # take the top 10 repos to measure depth
        sorted_projects = sorted(projects, key=lambda x: (x.get('lines') or x.get('estimated_lines') or 0), reverse=True)[:10]
        
        # First pass: calculate scores
        for p in sorted_projects:
            lines = p.get('lines') or p.get('estimated_lines') or 0
            is_fork = p.get('is_fork') or p.get('fork') or False
            multiplier = 1.5 if is_fork else 1.0
            repo_score = lines * multiplier
            project_complexities.append(repo_score)

        raw_avg = sum(project_complexities) / len(project_complexities) if project_complexities else 0.0
        batch_max = candidate_data.get('batch_max_complexity', 1.0)
        final_score = min(1.0, raw_avg / batch_max) if batch_max > 0 else 0.0
        
        # Second pass: build audit signals
        source_details = [
            {
                "name": "Composite Depth",
                "source": "GitHub Signal",
                "score": round(final_score, 2),
                "explanation": f"Average complexity of {int(raw_avg):,} units relative to batch peak."
            }
        ]
        
        for i, p in enumerate(sorted_projects):
            lines = p.get('lines') or p.get('estimated_lines') or 0
            is_fork = p.get('is_fork') or p.get('fork') or False
            multiplier = 1.5 if is_fork else 1.0
            repo_score = project_complexities[i]
            
            p_name = p.get('name', 'Unknown')
            status = "Contrib" if is_fork else "Original"
            explanation = f"{p_name}: {lines:,} Lines * {multiplier}x ({status}) = {int(repo_score):,} Pts"

            source_details.append({
                "name": p_name,
                "source": f"Project Detail: {p_name}",
                "score": 1.0 if repo_score > 0 else 0.0,
                "explanation": explanation
            })

        # check if the data is a bit stale
        is_stale_data = final_score == 0 and gh_data.get('total_lines', 0) > 0
        
        tech_formula = f"Average({int(raw_avg):,} Pts) / BatchPeak({int(batch_max):,} Pts) = {final_score:.2f}"
        if is_stale_data:
            tech_formula = "Historical data detected: Granular per-repo volumes missing. Please Re-Scrape candidate."

        return {
            "score": round(final_score, 2),
            "raw_complexity_sum": raw_avg,
            "breakdown": [
                {
                    "component": "Architectural Scale & Depth",
                    "score": round(final_score, 2),
                    "notes": "Detailed repository volume not found in historical data. Please Re-Scrape to enable granular analysis." if is_stale_data else f"Relative engineering depth compared to batch peak of {int(batch_max):,} complexity units.",
                    "source_details": [s for s in source_details if "Signal" in s["source"]] + sorted([s for s in source_details if "Detail" in s["source"]], key=lambda x: x['score'], reverse=True)[:8]
                }
            ],
            "sources_used": ["GitHub"],
            "calculation_formula": "Complexity Points = (Lines * ForkBonus). Multiplier: 1.5x for contributing to existing systems (forks). Final Score = Your Top 10 average vs Batch Peak.",
            "technical_formula": tech_formula,
            "glossary": [],
            "improvements": [i for i in [
                {"text": "Contribute to larger, existing systems (forks) to demonstrate architectural navigation skills.", "gain": 0.25} if not any(p.get('is_fork') or p.get('fork') for p in projects) else None,
                {"text": "Focus on developing deep, large-scale original projects to match the batch leaders.", "gain": 0.2} if final_score < 0.7 else None
            ] if i is not None]
        }


class GithubAlignmentMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "intel_github_alignment"
    
    @property
    def name(self) -> str:
        return "Ecosystem & Language Alignment"
        
    @property
    def description(self) -> str:
        return "Measures how well the candidate's GitHub language ecosystem aligns with the job requirements."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        gh_data = candidate_data.get('github_enriched', {})
        # DEBUG: See what the scoring engine actually sees
        # print(f"DEBUG: Scoring Candidate: {candidate_data.get('name')} | GH Data Keys: {list(gh_data.keys()) if gh_data else 'None'}")
        
        if not gh_data or not gh_data.get('languages'):
            # Don't return 0.0 here! We can still calculate alignment based on CV/LinkedIn signals
            # found in the other metrics. We only return 0 if there are NO requirements.
            pass
        
        # grab requirements and weights from the user config
        req_langs = {}
        jd_metrics = job_requirements.get("metrics", {})
        active_keys = candidate_data.get("active_keys", [])
        
        # Pull from "Languages" and "Technical Skills" buckets
        for category in ["Languages", "Technical Skills", "Technologies"]:
            items = jd_metrics.get(category, {}).get("value", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        name = str(item.get("name") or "").lower()
                        # Construct key matching the config format (snake_case)
                        skill_key = f"req_{name.replace(' ', '_').replace('-', '_')}"
                        
                        # ONLY consider items that are active in the CURRENT CONFIG
                        if skill_key not in active_keys:
                            continue
                            
                        weight = item.get("weight", 0)
                        if name: req_langs[name] = weight
                    else:
                        # Fallback for simple string lists
                        name = str(item).lower()
                        if name: req_langs[name] = 0
        
        if not any(k.startswith("req_") for k in active_keys):
            return {
                "score": 0.5,
                "breakdown": [],
                "sources_used": ["GitHub"],
                "calculation_formula": "Default",
                "technical_formula": "none",
                "glossary": [],
                "improvements": [{"text": "No specific technical requirements activated in Config.", "gain": 0.0}]
            }
            
        # map candidate proficiency (blends GitHub LOC and CV/LinkedIn skills)
        candidate_usage = {str(l.get('label') or '').lower(): l.get('pct', 0) for l in gh_data.get('languages', [])}
        all_skills = [str(s or "").lower() for s in candidate_data.get('skills', [])]
        li_skills = [str(s or "").lower() for s in candidate_data.get('linkedin_enriched', {}).get('skills', [])]
        combined_skills = set(all_skills + li_skills)
        
        total_weight = 0
        weighted_sum = 0
        audit_parts = []
        source_details = []
        skill_breakdown = []
        
        # Helper for case-insensitive weight lookup
        weights_map = {k.lower(): v for k, v in candidate_data.get("skill_weights", {}).items()}
        # Determine which requirements are actually active and weighted
        for key in active_keys:
            if not key.startswith("req_"):
                continue
                
            # clean the name for display
            display_name = key.replace("req_", "").replace("_", " ").capitalize()
            
            # get the weight from the config
            config_weight = weights_map.get(key.lower())
            if config_weight is None:
                continue
                
            math_weight = float(config_weight)
                      # get the pre-calculated score and full metric data from the first pass
            full_metric = candidate_data.get("skill_metrics", {}).get(key, {})
            metric_score = full_metric.get("score")
            
            multiplier = 0.0
            label = "None"
            
            if metric_score is not None:
                multiplier = metric_score
                label = f"Metric Score ({int(multiplier*100)}%)"
            else:
                lang_name = key.replace("req_", "").lower()
                pct = candidate_usage.get(lang_name, 0)
                if pct > 0:
                    multiplier = min(1.0, pct / 10.0)
                    label = f"Raw GitHub Signal ({int(multiplier*100)}%)"
                elif lang_name in combined_skills:
                    multiplier = 0.7
                    label = "CV/LI Validated"
            
            resolved_source = "CV"
            if "GitHub" in label: resolved_source = "GitHub"
            elif "LI" in label: resolved_source = "LinkedIn"

            # if the candidate has a large GitHub profile but it has ZERO overlap with their CV skills,
            # its a high-probability identity mismatch (e.g. felix fraud from evaluation/01_case study)
            # aggregate from usage map (fixed to look at all possible keys)
            gh_langs = {l.lower() for l, pct in candidate_usage.items() if pct > 5}
            if not gh_langs:
                # fallback to language_history if top-level is empty
                gh_hist = candidate_data.get("github_enriched", {}).get("language_history") or []
                gh_langs = {str(l.get("language") or "").lower() for l in gh_hist}

            if gh_langs and combined_skills:
                overlap = gh_langs.intersection(combined_skills)
                if not overlap and len(gh_langs) >= 1:
                    # caution: The profile is active but doesn't match the human at all.
                    # apply a 50% Tax for the data gap 
                    multiplier *= 0.5 
                    label = "IDENTITY MISMATCH WARNING (Suspicious Ecosystem)"

            weighted_sum += (math_weight * multiplier)
            total_weight += math_weight
            audit_parts.append(f"({display_name}: {multiplier:.2f} * {math_weight:.1f})")
            
            # construct breakdown item with simple audit data (no Bayesian jargon for this metric)
            notes_text = f"{display_name}: {label} | Weight: {math_weight:.1f}"
            explanation_text = f"This score is derived from the verified {display_name} expertise metric."
            is_warning = False
            if "WARNING" in label:
                is_warning = True
                explanation_text = f"CRITICAL: {label}. The system detected zero overlap between claimed CV skills and public GitHub artifacts. A 50% integrity multiplier has been applied."

            breakdown_item = {
                "item": display_name,
                "score": multiplier,
                "influence": math_weight,
                "weight": math_weight,
                "contribution": multiplier * math_weight,
                "notes": notes_text,
                "is_warning": is_warning,
                "status": "warning" if is_warning else "normal",
                "sources": ["System Intelligence"],
                "source_details": [{
                    "name": display_name,
                    "math_weight": math_weight,
                    "label": label if "WARNING" in label else f"{display_name} Match",
                    "source": "Metric Intelligence",
                    "score": multiplier,
                    "explanation": explanation_text,
                    "is_warning": is_warning
                }]
            }
            skill_breakdown.append(breakdown_item)
            source_details.append({
                "name": display_name,
                "score": multiplier,
                "math_weight": math_weight,
                "source": "Metric Intelligence"
            })

        total_weight = round(total_weight, 2)
        final_score = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0
        tech_formula = f"({' + '.join(audit_parts)}) / {total_weight} = {final_score:.2f}"
        
        # construct improvements and breakdown
        # Sort skills by actual score contribution for the breakdown: (score * weight)
        source_details.sort(key=lambda x: x["score"] * x["math_weight"], reverse=True)

        # sort by potential gain for the improvements
        skill_impacts = []
        for detail in source_details:
            potential_gain = (1.0 - detail["score"]) * (detail["math_weight"] / total_weight)
            if potential_gain > 0:
                skill_impacts.append({
                    "name": detail["name"],
                    "gain": potential_gain,
                    "weight": detail["math_weight"]
                })
        
        skill_impacts.sort(key=lambda x: x["gain"], reverse=True)
        
        improvements = []
        for impact in skill_impacts[:3]:
            gain_pct = int(impact["gain"] * 100)
            improvements.append({
                "text": f"Demonstrate proficiency in {impact['name']} (Priority {impact['weight']:.1f}) to boost match score by ~{gain_pct}%.",
                "gain": round(impact["gain"], 2),
                "variables": ["LanguageFit"]
            })
        
        if not improvements:
            improvements.append({"text": "Maximum ecosystem alignment achieved.", "gain": 0.0})

        # Determine if parent metric should have warning status
        parent_is_warning = any(item.get("is_warning") for item in skill_breakdown)

        return {
            "score": final_score,
            "status": "warning" if parent_is_warning else "normal",
            "is_warning": parent_is_warning,
            "breakdown": skill_breakdown,
            "weighted_average_breakdown": [
                {"name": b["item"], "score": b["score"], "weight": b["influence"]}
                for b in skill_breakdown
            ],
            "weighted_sum": weighted_sum,
            "total_weight": total_weight,
            "sources_used": ["GitHub", "CV", "LinkedIn"],
            "calculation_formula": "Σ(Skill_Match * Priority_Weight) / Total_Weight",
            "technical_formula": tech_formula,
            "glossary": [
                {
                    "variable": "LanguageFit",
                    "description": "How well their skills match the specific tech requirements.",
                    "impact": "High (Weight 0.8)",
                    "sensitivity": "Uses multi-source validation (GitHub LOC + CV/LI Claims)."
                }
            ],
            "improvements": improvements
        }

class GithubImpactMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "intel_github_impact"
    
    @property
    def name(self) -> str:
        return "Repository Stars & Community Impact"
        
    @property
    def description(self) -> str:
        return "Evaluates open-source community traction through stars, forks, and external PRs."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        gh_data = candidate_data.get('github_enriched', {})
        if not gh_data: return {"score": 0.0, "breakdown": [], "sources_used": ["GitHub"], "formula": "none", "technical_formula": "none", "glossary": [], "improvements": [{"text": "No GitHub data available", "gain": 0.0}]}
        
        stars = gh_data.get('total_stars') or 0
        forks = gh_data.get('total_forks') or 0
        
        # forks (2.5x) are worth more than stars (1.0x)
        raw_impact = (stars * 1.0) + (forks * 2.5)
        raw_log = math.log10(max(1, raw_impact + 1))
        
        # Relative Batch Scaling
        batch_max_impact = candidate_data.get('batch_max_impact', 10.0)
        max_log = math.log10(max(2, batch_max_impact + 1))
        
        score = min(1.0, raw_log / max_log) if max_log > 0 else 0.0
        
        return {
            "score": round(score, 2),
            "breakdown": [
                {
                    "component": "GitHub Adoption & Social Proof",
                    "score": round(score, 2),
                    "notes": f"Weighted impact of {raw_impact:.1f} pts ({stars}★, {forks} forks) relative to batch peak of {batch_max_impact:.1f} pts.",
                    "source_details": [
                        {
                            "source": "GitHub", 
                            "score": round(score, 2), 
                            "explanation": f"Impact Units: ({stars}★ * 1.0) + ({forks} forks * 2.5) = {raw_impact:.1f} pts. Scaled: log10({raw_impact:.1f}) / log10({batch_max_impact:.1f})"
                        }
                    ]
                }
            ],
            "sources_used": ["GitHub"],
            "calculation_formula": "log10(Weighted_Impact) / log10(Batch_Max_Impact)",
            "technical_formula": f"log10({raw_impact:.1f}) / log10({batch_max_impact:.1f}) = {score:.2f}",
            "glossary": [
                {
                    "variable": "Impact Units",
                    "description": "A weighted measure of community adoption, where 1 Fork = 2.5 Stars.",
                    "impact": "High (Primary measure of library adoption).",
                    "sensitivity": "Favors projects with deep developer engagement over simple popularity."
                }
            ],
            "improvements": [
                {
                    "text": f"The batch peak for impact is {batch_max_impact:.1f} units. Focus on driving code adoption (forks) to match the leaders.",
                    "gain": round(1.0 - score, 2)
                }
            ]
        }

class LinkedinExtracurricularMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "intel_linkedin_extracurricular"
    
    @property
    def name(self) -> str:
        return "Extracurricular Activity & Presence"
        
    @property
    def description(self) -> str:
        return "Assesses hackathons, publications, and professional volunteering presence."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        extra = candidate_data.get('extracurricular', []) or []
        li_data = candidate_data.get('linkedin_enriched', {})
        
        count = len(extra)
        if li_data.get('publications'): count += len(li_data['publications'])
        score = min(1.0, count / 3.0)
        
        return {
            "score": round(score, 2),
            "breakdown": [
                {
                    "name": "Community Presence",
                    "score": round(score, 2),
                    "source_details": [
                        {"source": "CV", "score": round(min(1.0, len(extra)/3.0), 2), "explanation": f"Detected {len(extra)} extra-curricular activities in CV."},
                        {"source": "LinkedIn", "score": 0.5 if li_data else 0.0, "explanation": "Found community activity signals on LinkedIn." if li_data else "No specific LinkedIn extracurriculars detected."}
                    ]
                }
            ],
            "sources_used": ["CV", "LinkedIn"],
            "calculation_formula": "count(Activities) / 3",
            "technical_formula": f"{count} / 3",
            "glossary": [],
            "improvements": ["Implement relevance scoring for activities"]
        }

class LinkedinNetworkMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "intel_linkedin_network"
    
    @property
    def name(self) -> str:
        return "Professional Network Size"
        
    @property
    def description(self) -> str:
        return "Evaluates the breadth of the candidate's professional network."
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: List[str] = None) -> Dict[str, Any]:
        li_data = candidate_data.get('linkedin_enriched', {})
        if not li_data: return {"score": 0.3, "breakdown": [], "sources_used": ["LinkedIn"], "formula": "none", "technical_formula": "none", "glossary": [], "improvements": ["No LinkedIn data available"]}
        
        connections = (li_data.get('connections') or 0)
        if connections == 0:
            connections = (li_data.get('followers') or 0)
            
        # log scaling for the network size
        raw_val = math.log10(max(1, connections))
        batch_max = candidate_data.get('batch_max_connections', 500)
        max_val = math.log10(max(2, batch_max))
        
        score = min(1.0, raw_val / max_val) if max_val > 0 else 0.0
        
        return {
            "score": round(score, 2),
            "breakdown": [
                {
                    "component": "Professional Network Gravity",
                    "score": round(score, 2),
                    "notes": f"Network reach of {connections:,} relative to batch peak of {batch_max:,} connections.",
                    "source_details": [
                        {"source": "LinkedIn", "score": round(score, 2), "explanation": f"Log-Scaled Reach: log10({connections:,}) / log10({batch_max:,}) = {score:.2f}"}
                    ]
                }
            ],
            "sources_used": ["LinkedIn"],
            "calculation_formula": "log10(Connections) / log10(BatchMax)",
            "technical_formula": f"log10({max(1, connections)}) / log10({max(1, batch_max)}) = {score:.2f}",
            "glossary": [],
            "improvements": [
                {
                    "text": f"The batch peak for network size is {batch_max:,} connections. Growing your professional network can increase your gravity score.",
                    "gain": round(1.0 - score, 2)
                }
            ]
        }
