from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS
from .semantic_utils import semantic_matcher
from core.fusion.bayesian import Evidence

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
        
        # work out the final multiplier
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

        total_item_score = 0.0
        for lang in target_languages:
            lang_lower = str(lang).lower()
            item_sources = []
            best_semantic = {}
            source_details = []
            
            # github signal (code volume)
            gh_pct = gh_languages.get(lang_lower, 0)
            gh_score = min(1.0, gh_pct / cfg["GH_VERIFICATION_THRESHOLD"])
            
            # cv signal (how many times they mention it)
            cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
            mentions = self._count_mentions(lang, cv_text)
            
            cv_score = 0.0
            if mentions > 0:
                # Scale score: 1 mention = 0.2, 2 = 0.4, 3 = 0.6, 4 = 0.8 (cap)
                cv_score = min(0.8, mentions * 0.2)
            else:
                # check for a semantic match in the technical skills section
                best_semantic = semantic_matcher.find_best_match(lang, list(set(cv_skills)), threshold=0.50)
                if best_semantic["match"]:
                    semantic_mentions = self._count_mentions(best_semantic["match"], cv_text)
                    cv_score = min(0.60, semantic_mentions * 0.15)
                    mentions = semantic_mentions # store for explanation block
            
            recency_mult, recency_note = self._calculate_recency_multiplier(lang, candidate_data)
            
            # --- Fusing evidence with probability ---
            # Bayesian model here to combine what they say on their CV with what's actually on GitHub.
            evidence = []
            conf = SCORING_CONSTANTS["FUSION"]["SOURCE_CONFIDENCE"]["TECHNICAL_SKILLS"]

            # GitHub Evidence
            if gh_pct > 0:
                item_sources.append("GitHub")
                evidence.append(Evidence(source="GitHub", confidence=conf["GITHUB"], strength=gh_score))
                source_details.append({
                    "source": "GitHub",
                    "score": gh_score,
                    "trust": conf["GITHUB"],
                    "derivation": f"min(1.0, {gh_pct}% / {cfg['GH_VERIFICATION_THRESHOLD']}%)",
                    "explanation": f"{gh_pct}% Code Density (Normalised: {gh_score:.2f})",
                    "weighting": f"Work Sample (Conf: {conf['GITHUB']:.1f})"
                })

            # CV Evidence
            if mentions > 0 or cv_score > 0:
                item_sources.append("CV")
                evidence.append(Evidence(source="CV", confidence=conf["CV"], strength=cv_score))
                explanation = f"{mentions} mentions" if not best_semantic.get("match") else f"Semantic Match: {best_semantic['match']} x{mentions}"
                source_details.append({
                    "source": "CV",
                    "score": cv_score,
                    "trust": conf["CV"],
                    "derivation": f"min({0.8 if not best_semantic.get('match') else 0.6}, {mentions} mentions * {0.2 if not best_semantic.get('match') else 0.15})",
                    "is_semantic_bridge": bool(best_semantic.get("match")),
                    "explanation": f"{explanation} (Normalised: {cv_score:.2f})",
                    "weighting": f"Self-reported (Conf: {conf['CV']:.1f})"
                })

            # LinkedIn Evidence
            li_experience = candidate_data.get("linkedin_experience") or []
            has_li = any(lang_lower in str(e.get("description") or "").lower() for e in li_experience)
            if has_li:
                item_sources.append("LinkedIn")
                evidence.append(Evidence(source="LinkedIn", confidence=conf["LINKEDIN"], strength=1.0))
                source_details.append({
                    "source": "LinkedIn",
                    "score": 1.0,
                    "trust": conf["LINKEDIN"],
                    "derivation": "Binary Presence (Mentions in role history = 1.0)",
                    "explanation": f"Mentioned in professional experience history. (Normalised: 1.00)",
                    "weighting": f"Historical Record (Conf: {conf['LINKEDIN']:.1f})"
                })

            # Temporal check (Skill Decay)
            if recency_mult < 1.0:
                # adding this as a negative signal to pull the score down if the skill is old
                decay_strength = 1.0 - recency_mult
                evidence.append(Evidence(source="Recency", confidence=conf["RECENCY"], strength=decay_strength, is_negative=True))
                source_details.append({
                    "source": "Temporal Decay Signal",
                    "score": -decay_strength,
                    "trust": conf["RECENCY"],
                    "explanation": f"{recency_note} (Decay applied to Bayesian model).",
                    "weighting": "Recency Audit"
                })

            # --- Run the actual fusion ---
            fusion_result = self._fuse_evidence(evidence)
            final_item_score = fusion_result["fused_score"]
            conf_label = fusion_result["confidence_label"]
            
            # Figure out which source is holding the candidate back
            weakest_source = "None"
            min_impact = 99.0
            if evidence:
                for ev in evidence:
                    impact = ev.strength * ev.confidence
                    if impact < min_impact and not ev.is_negative:
                        min_impact = impact
                        weakest_source = ev.source

            # Friendly summary for the recruiter
            if conf_label == "High Confidence":
                human_note = "Strong consensus across CV, LinkedIn, and GitHub."
            elif conf_label == "Medium Confidence":
                human_note = "Skill verified by multiple sources with slight variation."
            elif conf_label == "No Evidence":
                human_note = "No professional activity found for this skill."
            else:
                human_note = f"Warning: Conflicting signals. {weakest_source} data is the weakest link in this profile."

            total_item_score += final_item_score

            breakdown.append({
                "item": lang,
                "score": final_item_score,
                "uncertainty": fusion_result["uncertainty"],
                "confidence_label": conf_label,
                "bottleneck": weakest_source,
                "alpha": fusion_result["alpha"],
                "beta": fusion_result["beta"],
                "confidence_interval": fusion_result["confidence_interval"],
                "is_semantic_bridge": bool(best_semantic.get("match")),
                "source_details": source_details,
                "notes": f"{human_note} (Bayesian Audit: {fusion_result['logic']})",
                "sources": list(set(item_sources))
            })

        final_score = total_item_score / len(target_languages) if target_languages else 0
        
        # work out which formula to show in the UI
        if len(target_languages) == 1 and len(breakdown) == 1:
            tech_formula = breakdown[0]["notes"].replace("Logic: ", "")
        else:
            tech_formula = f"Avg({len(target_languages)} Items: {total_item_score:.2f} Total Points) = {final_score:.2f}"
        
        # --- Intelligent Improvement Analysis ---
        improvements = []
        if final_score < 0.95:
            remaining = 1.0 - final_score
            
            # Aggregate source performance across all skills
            source_scores = {} # source -> [scores]
            for b in breakdown:
                for sd in b.get("source_details", []):
                    src = sd.get("source")
                    if src not in source_scores: source_scores[src] = []
                    source_scores[src].append(sd.get("score", 0))
            
            avg_sources = {k: sum(v)/len(v) for k, v in source_scores.items()}
            
            # uncertainty Bottleneck
            any_uncertain = any(b.get("confidence_label") in ["Low Confidence", "Medium Confidence"] for b in breakdown)
            if any_uncertain:
                # most divergent source
                max_score = max(avg_sources.values()) if avg_sources else 1.0
                worst_src = min(avg_sources, key=avg_sources.get) if avg_sources else "CV"
                
                improvements.append({
                    "text": f"The Bayesian model detected uncertainty due to conflicting signals, primarily from the {worst_src} profile. Align your self-reported skill levels with your actual public work to reduce Beta (Uncertainty).",
                    "gain": remaining * 0.4,
                    "id": "BETA_UNCERTAINTY"
                })

            # Source-Specific Advice
            if avg_sources.get("GitHub", 1.0) < 0.8:
                improvements.append({
                    "text": f"Increase GitHub commit volume and line counts for the required languages ({', '.join(target_languages[:2])}) to boost the GH_Score variable (Alpha evidence).",
                    "gain": remaining * 0.3,
                    "id": "GH_SCORE"
                })
            
            if avg_sources.get("CV", 1.0) < 0.7:
                improvements.append({
                    "text": "Enhance your CV by providing more detailed role descriptions and explicit project achievements for these languages to improve heuristic strength.",
                    "gain": remaining * 0.2,
                    "id": "CV_STRENGTH"
                })

            if not improvements:
                improvements.append({
                    "text": "Demonstrate more consistent usage of these languages across all professional profiles to reach a High Confidence consensus.",
                    "gain": 0.05
                })
        else:
            improvements.append({"text": "Maximum proficiency score achieved across all required languages.", "gain": 0.0})

        return {
            "score": round(final_score, 2),
            "name": self.name,
            "id": self.id,
            "calculation_formula": "Bayesian_Fusion(GH_Density, CV_Mentions, LinkedIn_Record, Temporal_Prior)",
            "technical_formula": tech_formula,
            "breakdown": breakdown,
            "has_semantic_bridge": any(b.get("is_semantic_bridge") for b in breakdown),
            "sources_used": list(set([src for b in breakdown for src in b.get("sources", [])])),
            "glossary": [
                {"term": "Alpha (α)", "definition": "Strength of supporting evidence across all sources."},
                {"term": "Beta (β)", "definition": "Level of contradictory or missing signals causing uncertainty."}
            ],
            "improvements": improvements[:2]
        }
