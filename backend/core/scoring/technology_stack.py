from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS

class TechnologyStackMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "technologies"

    @property
    def name(self) -> str:
        return "Technology & Tool proficiency"

    @property
    def description(self) -> str:
        return "Analyses expertise in specific libraries, frameworks, and tools mentioned in the job description."

    def _calculate_recency_multiplier(self, tech: str, candidate_data: Dict[str, Any]) -> tuple[float, str]:
        import datetime
        current_year = datetime.datetime.now().year
        tech_lower = tech.lower()
        
        # Use language recency config as baseline
        cfg = SCORING_CONSTANTS["LANGUAGES"]["RECENCY"]
        
        # check github activity (scans repo names and descriptions for the tech)
        gh_profile = candidate_data.get("github_profile") or {}
        gh_repos = candidate_data.get("github_projects") or []
        last_gh_year = 0
        for repo in gh_repos:
            r_name = str(repo.get("name") or "").lower()
            r_desc = str(repo.get("description") or "").lower()
            if tech_lower in r_name or tech_lower in r_desc:
                # Approximate year from updated_at or similar
                u_at = repo.get("updated_at")
                if u_at and isinstance(u_at, str) and len(u_at) >= 4:
                    last_gh_year = max(last_gh_year, int(u_at[:4]))
        
        # then check linkedin history
        li_experience = candidate_data.get("linkedin_experience") or []
        last_li_year = 0
        for i, exp in enumerate(li_experience[:3]):
            desc = (exp.get("description") or "").lower()
            pos = (exp.get("position") or "").lower()
            if tech_lower in desc or tech_lower in pos:
                last_li_year = max(last_li_year, current_year - i)
        
        latest_activity = max(last_gh_year, last_li_year)
        if latest_activity == 0: 
            return 1.0, "Historical claim (No recent temporal activity)"
            
        years_since = current_year - latest_activity
        if years_since <= 1: return cfg["ACTIVE"], "Active Proficiency"
        if years_since == 2: return cfg["NEAR_RECENT"], "Slight Decay"
        if years_since == 3: return cfg["DECAY"], "Significant Decay"
        return cfg["LEGACY"], "Legacy Skill"

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        breakdown = []
        sources_used = ["CV"]
        cfg = SCORING_CONSTANTS["TECH_STACK"]
        
        jd_metrics = job_requirements.get("metrics", {})
        tech_config = jd_metrics.get("Technologies", {}).get("value", [])
        
        target_tech = tech_config
        if active_items:
            active_set = {a.lower() for a in active_items}
            target_tech = [t for t in tech_config if t.lower() in active_set]
            for a in active_items:
                if a.lower() not in {t.lower() for t in tech_config}:
                    target_tech.append(a)

        if not target_tech:
             return {"score": 0.0, "breakdown": [], "sources_used": sources_used}

        raw_skills = candidate_data.get("skills") or []
        cv_skills = [str(s).lower() for s in raw_skills if s is not None]
        li_exp = candidate_data.get("linkedin_experience", [])
        li_text = " ".join([str(e.get("description") or "") for e in li_exp]).lower()
        if li_exp: sources_used.append("LinkedIn")

        total_item_score = 0.0
        for tech in target_tech:
            tech_lower = str(tech).lower()
            
            has_cv = False
            match_evidence = None
            for s in cv_skills:
                if len(tech_lower) <= 3 or len(s) <= 3:
                    if tech_lower == s:
                        has_cv = True
                        match_evidence = s
                        break
                else:
                    if tech_lower in s or s in tech_lower:
                        has_cv = True
                        match_evidence = s
                        break
            
            has_li = tech_lower in li_text and len(tech_lower) > 2
            
            item_sources = []
            source_details = [
                {
                    "name": tech,
                    "source": f"Tooling Detail: {tech}",
                    "score": 1.0 if (has_cv or has_li) else 0.0,
                    "explanation": f"Analysing professional footprint for {tech}."
                }
            ]
            
            if has_li:
                item_sources.append("LinkedIn")
                start_idx = max(0, li_text.find(tech_lower) - 40)
                end_idx = min(len(li_text), li_text.find(tech_lower) + 60)
                snippet = li_text[start_idx:end_idx].strip()
                source_details.append({
                    "source": "LinkedIn Signal",
                    "score": 0.70,
                    "explanation": f"Found in experience: \"...{snippet}...\"",
                    "weighting": "Primary significance (Historical Record)"
                })

            if has_cv:
                item_sources.append("CV")
                evidence_str = match_evidence if match_evidence else tech_lower
                source_details.append({
                    "source": "CV Signal",
                    "score": 0.50,
                    "explanation": f"Explicitly listed as: \"{evidence_str}\"",
                    "weighting": "Self-reported claim (Baseline)"
                })
            
            recency_mult, recency_note = self._calculate_recency_multiplier(tech, candidate_data)
            source_details.append({
                "source": "Temporal Analysis Signal",
                "score": recency_mult,
                "explanation": f"{recency_note} (Factor: {recency_mult}x)",
                "weighting": "Recency Audit"
            })

            base_score = 0.70 if has_li else (0.50 if has_cv else 0.0)
            item_score = self._calculate_multi_source_bonus(item_sources, base_score)
            final_item_score = self._normalise_score(item_score * recency_mult)
            
            total_item_score += final_item_score
            breakdown.append({
                "item": tech,
                "score": final_item_score,
                "source_details": source_details,
                "notes": f"Logic: ({item_score:.2f} base) * {recency_mult}x recency = {final_item_score:.2f}",
                "sources": list(set(item_sources))
            })

        final_score = total_item_score / len(target_tech) if target_tech else 0
        
        # determining technical formula
        if len(target_tech) == 1 and len(breakdown) == 1:
            tech_formula = breakdown[0]["notes"].replace("Logic: ", "")
        else:
            tech_formula = f"Avg({total_item_score:.2f} Total Points / {len(target_tech)} Items) = {final_score:.2f}"

        improvements = []
        if final_score < 1.0:
            remaining = 1.0 - final_score
            avg_cv = sum(1 for b in breakdown if "CV" in b["sources"]) / len(breakdown) if breakdown else 0
            avg_li = sum(1 for b in breakdown if "LinkedIn" in b["sources"]) / len(breakdown) if breakdown else 0
            has_low_recency = any(s.get("source") == "Temporal Analysis Signal" and s.get("score", 1.0) < 1.0 for b in breakdown for s in b.get("source_details", []))

            if avg_cv < 1.0:
                improvements.append({"text": "Explicitly list the exact framework/tool keywords in the CV skills section or experience bullet points.", "gain": remaining * 0.4, "variables": ["CVSignal"]})
            if avg_li < 1.0:
                improvements.append({"text": "Mention the required tools in your most recent LinkedIn experience descriptions to gain a multi-source verification bonus.", "gain": remaining * 0.3, "variables": ["LinkedInSignal"]})
            if has_low_recency:
                improvements.append({"text": "Update your profile with recent projects using these tools to improve the temporal multiplier.", "gain": remaining * 0.3, "variables": ["Recency_Factor"]})
            
            if not improvements:
                improvements.append({"text": "Ensure your technology stack perfectly aligns with the job description.", "gain": remaining, "variables": []})
        else:
            improvements.append({"text": "Maximum technology stack score achieved.", "gain": 0.0, "variables": []})

        return {
            "score": self._normalise_score(final_score),
            "calculation_formula": "(max(LinkedInSignal, CVSignal) * ConsensusMultiplier) * Recency_Factor",
            "technical_formula": tech_formula,
            "glossary": [
                {
                    "variable": "LinkedInSignal",
                    "description": "Checks if they've actually mentioned this in their work history on LinkedIn.",
                    "impact": "High-confidence signal (0.70 baseline).",
                    "sensitivity": "Might be low if it's not mentioned in their last couple of roles."
                },
                {
                    "variable": "CVSignal",
                    "description": "Looks for the tool or framework explicitly listed in the CV.",
                    "impact": "Self-reported baseline (0.50).",
                    "sensitivity": "Sensitive to spelling differences or missing keywords."
                },
                {
                    "variable": "Recency_Factor",
                    "description": "A multiplier that drops if they haven't used the tool recently.",
                    "impact": "Scales score based on how long ago the tool was last used.",
                    "sensitivity": "Starts dropping quite a bit after 3 years of no activity."
                }
            ],
            "breakdown": breakdown,
            "sources_used": list(set(sources_used)),
            "improvements": improvements[:3]
        }
