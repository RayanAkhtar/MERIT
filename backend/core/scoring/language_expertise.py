import math
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
        
        # github recency check using weighted average to catch past peaks
        gh_profile = candidate_data.get("github_profile") or {}
        gh_history = gh_profile.get("language_history") or []
        
        weighted_gh_sum = 0
        total_gh_volume = 0
        last_gh_year = 0
        
        for entry in gh_history:
            year = int(entry.get("year", 0))
            volume = 0
            for k, v in entry.items():
                if str(k).lower() == lang_lower:
                    volume = float(v or 0)
                    break
            
            if volume > 0:
                weighted_gh_sum += (year * volume)
                total_gh_volume += volume
                last_gh_year = max(last_gh_year, year)
        
        effective_gh_year = weighted_gh_sum / total_gh_volume if total_gh_volume > 0 else 0
        
        # linkedin recency check
        li_experience = candidate_data.get("linkedin_experience") or []
        last_li_year = 0
        for i, exp in enumerate(li_experience[:2]):
            desc = (exp.get("description") or "").lower()
            pos = (exp.get("position") or "").lower()
            if lang_lower in desc or lang_lower in pos:
                last_li_year = max(last_li_year, current_year - i)
        
        # calculate the multiplier using exponential decay
        latest_activity = max(effective_gh_year, float(last_li_year))
        if latest_activity == 0: 
            return 1.0, "Historical claim (No recent temporal data)"
            
        years_since = float(current_year - latest_activity)
        
        #  exponential decay
        decay_mult = math.exp(-cfg["DECAY_LAMBDA"] * years_since)
        
        if years_since <= cfg["ACTIVE_THRESHOLD"]:
            return cfg["BOOST_ACTIVE"], f"Active Proficiency (Last seen {latest_activity})"
        
        decay_mult = round(decay_mult, 2)
        
        if years_since <= 3:
            return decay_mult, f"Temporal Decay (Last used ~{int(years_since)} years ago)"
        
        return max(0.2, decay_mult), f"Legacy Skill ({int(years_since)}+ years since last activity)"

    def _count_mentions(self, lang: str, cv_text: str) -> int:
        if not cv_text: return 0
        import re
        lang_lower = lang.lower()

        # count occurrences with word boundaries to avoid substrings
        pattern = rf"\b{re.escape(lang_lower)}\b"
        return len(re.findall(pattern, cv_text.lower()))
        
    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None) -> Dict[str, Any]:
        import datetime
        current_year = datetime.datetime.now().year
        breakdown = []
        sources_used = ["CV"]
        cfg = SCORING_CONSTANTS["LANGUAGES"]
        
        # get languages from JD
        jd_metrics = job_requirements.get("metrics", {})
        languages_config = jd_metrics.get("Languages", {}).get("value", [])
        
        target_languages = languages_config
        if active_items:
            active_set = {str(a).lower() for a in active_items if a is not None}
            # Extract names from config if they are dictionaries
            target_languages = []
            for l in languages_config:
                l_val = l.get("value") if isinstance(l, dict) else l
                if l_val and str(l_val).lower() in active_set:
                    target_languages.append(l)
            
            for a in active_items:
                if a and str(a).lower() not in {str(l.get("value") if isinstance(l, dict) else l).lower() for l in languages_config if l is not None}:
                    target_languages.append(a)

        if not target_languages:
             return {"score": 0.0, "breakdown": [], "sources_used": sources_used}

        gh_profile = candidate_data.get("github_profile") or {}
        gh_languages = {}
        gh_history = gh_profile.get("language_history") or []
        if gh_profile:
            sources_used.append("GitHub")
            gh_raw = gh_profile.get("languages") or []
            gh_languages = {str(l.get("label") or "").lower(): (l.get("pct") or 0) for l in gh_raw if isinstance(l, dict)}

        raw_skills = candidate_data.get("skills") or []
        cv_skills = [str(s).lower() for s in raw_skills if s is not None]

        total_item_score = 0.0
        for lang in target_languages:
            # item could be a string or a dict {"value": "Python", ...}
            lang_val = lang.get("value") if isinstance(lang, dict) else lang
            lang_lower = str(lang_val).lower()
            
            # also extract the item name for the breakdown display
            lang_display = lang_val

            item_sources = []
            best_semantic = {}
            source_details = []
            
            # github signal (code volume + temporal weighting)
            gh_pct = gh_languages.get(lang_lower, 0)
            
            # github recency for this language
            gh_weighted_sum = 0
            gh_total_vol = 0
            for entry in gh_history:
                year = int(entry.get("year", 0))
                # case insensitive lookup for the language volume
                vol = 0
                for k, v in entry.items():
                    if str(k).lower() == lang_lower:
                        vol = float(v or 0)
                        break
                
                if vol > 0:
                    gh_weighted_sum += (year * vol)
                    gh_total_vol += vol
            
            gh_effective_year = gh_weighted_sum / gh_total_vol if gh_total_vol > 0 else 0
            gh_years_since = float(current_year - gh_effective_year) if gh_effective_year > 0 else 0
            
            # apply github decay to the volume score
            gh_decay = math.exp(-cfg["RECENCY"]["DECAY_LAMBDA"] * gh_years_since)
            gh_score = min(1.0, (gh_pct / cfg["GH_VERIFICATION_THRESHOLD"]) * gh_decay)
            
            # cv signal (how many times they mention it)
            cv_text = candidate_data.get("raw_cv_text") or candidate_data.get("full_cv_text") or ""
            mentions = self._count_mentions(lang_val, cv_text)

            
            cv_score = 0.0
            if mentions > 0:
                cv_score = min(0.8, mentions * 0.2)
            else:
                # semantic match in technical skills
                best_semantic = semantic_matcher.find_best_match(lang_val, list(set(cv_skills)), threshold=0.50)

                if best_semantic["match"]:
                    semantic_mentions = self._count_mentions(best_semantic["match"], cv_text)
                    cv_score = min(0.60, semantic_mentions * 0.15)
                    mentions = semantic_mentions # store for explanation block
            
            recency_mult, recency_note = self._calculate_recency_multiplier(lang_val, candidate_data)

            
            # fusing evidence with probability
            evidence = []
            conf = SCORING_CONSTANTS["FUSION"]["SOURCE_CONFIDENCE"]["TECHNICAL_SKILLS"]

            # github evidence
            if gh_pct > 0:
                item_sources.append("GitHub")
                evidence.append(Evidence(source="GitHub", confidence=conf["GITHUB"], strength=gh_score))
                source_details.append({
                    "source": "GitHub",
                    "score": gh_score,
                    "trust": conf["GITHUB"],
                    "derivation": f"({gh_pct:.1f}% / {cfg['GH_VERIFICATION_THRESHOLD']:.0f}% Threshold) * {gh_decay:.2f} (Temporal Weight)",
                    "explanation": f"Found {gh_pct:.1f}% code volume on GitHub. Last significant activity (Weighted Center): {gh_effective_year:.1f}.",
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
                evidence.append(Evidence(source="LinkedIn", confidence=conf["LINKEDIN"], strength=0.8))
                source_details.append({
                    "source": "LinkedIn",
                    "score": 0.8,
                    "trust": conf["LINKEDIN"],
                    "derivation": "Binary Presence (Mentions in role history = 0.8 Cap)",
                    "explanation": f"Mentioned in professional experience history. (Normalised: 0.80)",
                    "weighting": f"Historical Record (Conf: {conf['LINKEDIN']:.1f})"
                })

            # temporal check (skill decay)
            decay_penalty = max(0, 1.0 - recency_mult)
            if decay_penalty > 0:
                evidence.append(Evidence(source="Recency", confidence=conf["RECENCY"], strength=decay_penalty, is_negative=True))
            
            source_details.append({
                "source": "Temporal Audit",
                "score": -decay_penalty if decay_penalty > 0 else 1.0,
                "trust": conf["RECENCY"],
                "explanation": f"{recency_note} (Multiplier: {recency_mult:.2f})",
                "weighting": "Recency Check"
            })

            # run the actual fusion
            fusion_result = self._fuse_evidence(evidence)
            final_item_score = fusion_result["fused_score"]
            conf_label = fusion_result["confidence_label"]
            
            # figure out which source is holding the candidate back
            weakest_source = "None"
            min_impact = 99.0
            if evidence:
                for ev in evidence:
                    impact = ev.strength * ev.confidence
                    if impact < min_impact and not ev.is_negative:
                        min_impact = impact
                        weakest_source = ev.source

            # summary for the recruiter
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
                "item": lang_display,
                "score": final_item_score,
                "uncertainty": fusion_result["uncertainty"],
                "confidence_label": conf_label,
                "confidence_reason": fusion_result.get("confidence_reason"),
                "bottleneck": weakest_source,
                "alpha": fusion_result["alpha"],
                "beta": fusion_result["beta"],
                "confidence_interval": fusion_result["confidence_interval"],
                "is_semantic_bridge": bool(best_semantic.get("match")),
                "source_details": source_details,
                "temporal_formula": "S_{decay} = S_{base} \cdot e^{-\lambda \Delta t}",
                "temporal_params": {
                    "lambda": cfg["RECENCY"]["DECAY_LAMBDA"], 
                    "delta_t": round(current_year - gh_effective_year, 2) if gh_effective_year > 0 else 0,
                    "weight": round(gh_decay, 2)
                },
                "notes": f"{human_note} (Bayesian Audit: {fusion_result['logic']})",
                "sources": list(set(item_sources))
            })

        final_score = total_item_score / len(target_languages) if target_languages else 0
        
        # work out which formula to show in the UI
        if len(target_languages) == 1 and len(breakdown) == 1:
            tech_formula = breakdown[0]["notes"].replace("Logic: ", "")
        else:
            tech_formula = f"Avg({len(target_languages)} Items: {total_item_score:.2f} Total Points) = {final_score:.2f}"
        
        # intelligent improvement analysis
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
                display_langs = [l.get("value") if isinstance(l, dict) else l for l in target_languages[:2]]
                improvements.append({
                    "text": f"Increase GitHub commit volume and line counts for the required languages ({', '.join(display_langs)}) to boost the GH_Score variable (Alpha evidence).",
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
