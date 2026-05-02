from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS

class LanguageExpertiseMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "languages"

    @property
    def name(self) -> str:
        return "Programming Language Proficiency"

    @property
    def description(self) -> str:
        return "Cross-references claimed programming languages with actual GitHub code volume and repository activity."

    def _calculate_recency_multiplier(self, lang: str, candidate_data: Dict[str, Any]) -> tuple[float, str]:
        import datetime
        current_year = datetime.datetime.now().year
        lang_lower = lang.lower()
        
        cfg = SCORING_CONSTANTS["LANGUAGES"]["RECENCY"]
        
        # github recency check
        gh_profile = candidate_data.get("github_profile") or {}
        gh_history = gh_profile.get("language_history") or []
        last_gh_year = 0
        for entry in gh_history:
            year = int(entry.get("year", 0))
            if any(str(k).lower() == lang_lower and (v or 0) > 0 for k, v in entry.items()):
                last_gh_year = max(last_gh_year, year)
        
        # linkedin recency check
        li_experience = candidate_data.get("linkedin_experience") or []
        last_li_year = 0
        for i, exp in enumerate(li_experience[:2]):
            desc = (exp.get("description") or "").lower()
            pos = (exp.get("position") or "").lower()
            if lang_lower in desc or lang_lower in pos:
                last_li_year = max(last_li_year, current_year - i)
        
        # final multiplier logic
        latest_activity = max(last_gh_year, last_li_year)
        if latest_activity == 0: 
            return 1.0, "Historical claim (No recent temporal data)"
            
        years_since = current_year - latest_activity
        
        if years_since <= 1:
            return cfg["ACTIVE"], "Active Proficiency (Used in current/recent cycle)"
        if years_since == 2:
            return cfg["NEAR_RECENT"], "Slight Decay (Last seen ~2 years ago)"
        if years_since == 3:
            return cfg["DECAY"], "Significant Decay (Moving away from technology)"
        
        return cfg["LEGACY"], "Legacy Skill (No activity in 4+ years)"

    def _count_mentions(self, lang: str, cv_text: str) -> int:
        if not cv_text: return 0
        import re
        lang_lower = lang.lower()
        # count occurrences with word boundaries to avoid substrings
        pattern = rf"\b{re.escape(lang_lower)}\b"
        return len(re.findall(pattern, cv_text.lower()))

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        breakdown = []
        sources_used = ["CV"]
        cfg = SCORING_CONSTANTS["LANGUAGES"]
        
        # get languages from JD
        jd_metrics = job_requirements.get("metrics", {})
        languages_config = jd_metrics.get("Languages", {}).get("value", [])
        
        target_languages = languages_config
        if active_items:
            active_set = {str(a).lower() for a in active_items if a is not None}
            target_languages = [l for l in languages_config if l and str(l).lower() in active_set]
            for a in active_items:
                if a and str(a).lower() not in {str(l).lower() for l in languages_config if l is not None}:
                    target_languages.append(a)

        if not target_languages:
             return {"score": 0.0, "breakdown": [], "sources_used": sources_used}

        gh_profile = candidate_data.get("github_profile")
        gh_languages = {}
        if gh_profile:
            sources_used.append("GitHub")
            gh_raw = gh_profile.get("languages") or []
            gh_languages = {str(l.get("label") or "").lower(): (l.get("pct") or 0) for l in gh_raw if isinstance(l, dict)}

        raw_skills = candidate_data.get("skills") or []
        cv_skills = [str(s).lower() for s in raw_skills if s is not None]
        from collections import Counter
        mention_counts = Counter(cv_skills)
        max_cv_mentions = max(mention_counts.values()) if mention_counts else 0

        total_item_score = 0.0
        for lang in target_languages:
            lang_lower = str(lang).lower()
            item_sources = []
            
            # github signal
            # print(f"DEBUG: {lang} github pct -> {gh_pct}")
            gh_pct = gh_languages.get(lang_lower, 0)
            gh_score = min(1.0, gh_pct / cfg["GH_VERIFICATION_THRESHOLD"])
            if gh_pct > 0: item_sources.append("GitHub")
            
            # cv Signal
            cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
            mentions = self._count_mentions(lang, cv_text)
            
            cv_score = 0.0
            prominence_note = ""
            if mentions > 0:
                # Scale score: 1 mention = 0.2, 2 = 0.4, 3 = 0.6, 4 = 0.8 (cap)
                cv_score = min(0.8, mentions * 0.2)
                item_sources.append("CV")
            
            recency_mult, recency_note = self._calculate_recency_multiplier(lang, candidate_data)
            
            primary_score = max(gh_score, cv_score)
            item_score = self._calculate_multi_source_bonus(item_sources, primary_score)
            final_item_score = self._normalise_score(item_score * recency_mult)
            
            total_item_score += final_item_score
            
            # Mathematical Transparency
            bonus_val = 1.15 if len(set(item_sources)) > 1 else 1.0
            logic_summary = f"(max({gh_score:.2f}, {cv_score:.2f}) * {bonus_val:.2f}) * {recency_mult:.1f} = {final_item_score:.2f}"
            
            source_details = [
                {
                    "name": lang,
                    "source": f"Tooling Detail: {lang}",
                    "score": final_item_score,
                    "explanation": f"Validated {lang} proficiency across professional signals."
                }
            ]
            if gh_pct > 0:
                source_details.append({
                    "source": "GitHub Signal",
                    "score": gh_score,
                    "explanation": f"{gh_pct}% Lines of Code (Normalised: {gh_score:.2f})",
                    "weighting": f"Harsher Heuristic: {gh_pct}% / {cfg['GH_VERIFICATION_THRESHOLD']}% (cap 1.0)"
                })
            if mentions > 0:
                source_details.append({
                    "source": "CV Signal",
                    "score": cv_score,
                    "explanation": f"{mentions} mentions{prominence_note} (Normalised: {cv_score:.2f})",
                    "weighting": f"Heuristic: ({mentions}*0.2) * {'Penalty' if prominence_note else '1.0'} Prominence"
                })
            
            source_details.append({
                "source": "Temporal Analysis Signal",
                "score": recency_mult,
                "explanation": f"{recency_note} (Factor: {recency_mult}x)",
                "weighting": "Recency Audit (GitHub/LinkedIn Timeline)"
            })

            breakdown.append({
                "item": lang,
                "score": final_item_score,
                "source_details": source_details,
                "notes": f"Logic: {logic_summary}",
                "sources": list(set(item_sources))
            })

        final_score = total_item_score / len(target_languages) if target_languages else 0
        
        # Determine technical formula: show aggregate if multi-item, show specific if single-item
        if len(target_languages) == 1 and len(breakdown) == 1:
            tech_formula = breakdown[0]["notes"].replace("Logic: ", "")
        else:
            # Construct a clear summation formula for the aggregate view
            formula_parts = []
            for item in breakdown:
                # Extract the core math from the item notes (e.g., "(max(...) + ...) * ...")
                core_math = item["notes"].replace("Logic: ", "").split(" = ")[0]
                formula_parts.append(f"{core_math} [{item['item']}]")
            
            joined_parts = " + ".join(formula_parts)
            if len(target_languages) > 2:
                # If too many items, show a summary version to keep the UI clean
                tech_formula = f"Avg({len(target_languages)} Items: {total_item_score:.2f} Total Points) = {final_score:.2f}"
            else:
                tech_formula = f"Avg({joined_parts}) = {final_score:.2f}"
        
        improvements = []
        if final_score < 1.0:
            remaining = 1.0 - final_score
            avg_gh = sum(1 for b in breakdown if "GitHub" in b["sources"]) / len(breakdown) if breakdown else 0
            avg_cv = sum(1 for b in breakdown if "CV" in b["sources"]) / len(breakdown) if breakdown else 0
            avg_recency = sum(1 for b in breakdown if any("Temporal" in str(s.get("source", "")) for s in b.get("source_details", []))) / len(breakdown) if breakdown else 0
            # Note: The above avg_recency check isn't perfectly accurate since recency mult is numeric, but we can just check if any recency mult < 1.0
            has_low_recency = any("Temporal" in str(s.get("source", "")) and s.get("score", 1.0) < 1.0 for b in breakdown for s in b.get("source_details", []))

            if avg_gh < 1.0:
                improvements.append({"text": "Increase GitHub commit volume and line counts for the required languages to boost the code density signal.", "gain": remaining * 0.4, "variables": ["GH_Score"]})
            if avg_cv < 1.0:
                improvements.append({"text": "Ensure the required languages are prominently mentioned across both CV skills and recent LinkedIn roles.", "gain": remaining * 0.3, "variables": ["CV_Score"]})
            if has_low_recency or (avg_gh == 1.0 and avg_cv == 1.0):
                improvements.append({"text": "Contribute to repositories using the required languages recently to improve the temporal recency multiplier.", "gain": remaining * 0.3, "variables": ["Recency_Factor"]})
                
            if not improvements:
                improvements.append({"text": "Ensure your language stack perfectly aligns with the job description.", "gain": remaining, "variables": []})
        else:
            improvements.append({"text": "Maximum proficiency score achieved across all required languages.", "gain": 0.0, "variables": []})

        return {
            "score": self._normalise_score(final_score),
            "calculation_formula": f"(max(GH_Score, CV_Score) * ConsensusMultiplier) * Recency_Factor",
            "technical_formula": tech_formula,
            "glossary": [
                {
                    "variable": "GH_Score",
                    "description": "How much code in this language is on their GitHub.",
                    "impact": f"High impact (threshold is {cfg['GH_VERIFICATION_THRESHOLD']}%).",
                    "sensitivity": "low if there's no public code."
                },
                {
                    "variable": "CV_Score",
                    "description": "How often the language appears in the CV.",
                    "impact": "baseline verification.",
                    "sensitivity": "low if the skill is just a footnote."
                },
                {
                    "variable": "ConsensusMultiplier",
                    "description": "Bonus for finding the skill in two places.",
                    "impact": "1.15x boost for cross-verification.",
                    "sensitivity": "n/a"
                },
                {
                    "variable": "Recency_Factor",
                    "description": "Penalty for skills not used in years.",
                    "impact": "Can cut the score if it's a 'legacy' skill.",
                    "sensitivity": "High if they haven't used it since uni."
                }
            ],
            "breakdown": breakdown,
            "sources_used": list(set(sources_used)),
            "improvements": improvements[:3]
        }
