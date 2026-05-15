from typing import Dict, Any, List, Optional
from .base import BaseMetric
from .constants import SCORING_CONSTANTS

class EducationMetric(BaseMetric):
    @property
    def id(self) -> str:
        return "education"

    @property
    def name(self) -> str:
        return "Educational Qualifications"

    @property
    def description(self) -> str:
        return "Evaluates degree level and school prestige by cross-referencing CV data with LinkedIn education records."

    def calculate(self, candidate_data: Dict[str, Any], job_requirements: Dict[str, Any], active_items: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        breakdown = []
        sources_used = ["CV"]
        
        # check what the job description actually wants
        jd_metrics = job_requirements.get("metrics", {})
        edu_reqs = jd_metrics.get("Education", {}).get("value", [])
        
        # grab candidate info from both CV and LinkedIn
        cv_edu = candidate_data.get("cv_education", [])
        li_edu = candidate_data.get("linkedin_education", [])
        if li_edu: sources_used.append("LinkedIn")
        
        # Combine all educational records
        all_edu = cv_edu + li_edu
        
        # matching logic: PhD > Masters > Bachelors
        # (PhD > Masters > Bachelors)
        degree_hierarchy = {"phd": 3, "doctorate": 3, "msc": 2, "masters": 2, "meng": 2, "bsc": 1, "bachelors": 1, "beng": 1}
        
        max_candidate_level = 0
        best_school = "Unknown"
        
        for edu in all_edu:
            degree_str = (edu.get("degree") or "").lower()
            current_level = 0
            for key, level in degree_hierarchy.items():
                if key in degree_str:
                    current_level = max(current_level, level)
            
            if current_level > 0:
                if current_level >= max_candidate_level:
                    max_candidate_level = current_level
                    # only update best_school if this is a degree-level entry
                    best_school = edu.get("school_name", "Unknown")
            elif best_school == "Unknown":
                # fallback if we haven't found a degree level yet
                best_school = edu.get("school_name", "Unknown")

        if max_candidate_level == 0 and all_edu:
            max_candidate_level = 1 # Assume Bachelors if an education entry exists but level couldn't be parsed


        # university prestige and grades logic
        import json, os
        cfg = SCORING_CONSTANTS["EDUCATION"]
        prestige_bonus = 0.0
        prestige_note = "Standard Institution"
        
        try:
            with open(os.path.join(os.path.dirname(__file__), "..", "parsers", "universities_data.json"), "r") as f:
                uni_data = json.load(f)
                tiers = uni_data.get("tiers", {})
                for tier, schools in tiers.items():
                    if any(s.lower() in best_school.lower() for s in schools):
                        if tier == "tier_1": prestige_bonus, prestige_note = cfg["PRESTIGE_BONUS"]["TIER_1"], "Tier 1 (Global Elite)"
                        elif tier == "tier_2": prestige_bonus, prestige_note = cfg["PRESTIGE_BONUS"]["TIER_2"], "Tier 2 (High Prestige)"
                        elif tier == "tier_3": prestige_bonus, prestige_note = cfg["PRESTIGE_BONUS"]["TIER_3"], "Tier 3 (Russell Group)"
                        break
        except: pass

        grade_cfg = cfg["GRADE_MULTIPLIER"]
        grade_multiplier = grade_cfg["DEFAULT"]
        grade_label = "2:1 (Assumed)"
        all_grades = [str(edu.get("grade") or "").lower() for edu in all_edu]
        for g in all_grades:
            if "1st" in g or "first" in g or "70" in g or "4.0" in g:
                grade_multiplier, grade_label = grade_cfg["FIRST_CLASS"], "1st Class / 1:1"
                break
            elif "2:1" in g or "upper" in g or "60" in g or "3.5" in g:
                grade_multiplier, grade_label = grade_cfg["UPPER_SECOND"], "Upper Second (2:1)"
            elif "2:2" in g or "lower" in g or "50" in g:
                grade_multiplier = max(grade_multiplier, grade_cfg["LOWER_SECOND"])
                if grade_multiplier == grade_cfg["LOWER_SECOND"]: grade_label = "Lower Second (2:2)"

        # check if they meet the JD's minimum
        target_level = 1 # Default to Bachelors
        jd_metrics = job_requirements.get("metrics", {})
        if "Education" in jd_metrics:
            edu_vals = jd_metrics["Education"].get("value", [])
            # Combine all text from education requirements to find degree level
            target_str = ""
            for v in edu_vals:
                if isinstance(v, dict):
                    target_str += " " + str(v.get("value", "")).lower()
                else:
                    target_str += " " + str(v).lower()
            
            if "phd" in target_str or "doctor" in target_str: target_level = 3
            elif "master" in target_str or "meng" in target_str or "msc" in target_str: target_level = 2

        # work out the final weighted score
        level_map = {0: "None", 1: "Bachelors", 2: "Masters/MEng", 3: "PhD/Doctorate"}
        level_score = 1.0 if max_candidate_level >= target_level else (0.5 if max_candidate_level > 0 else 0.0)
        note = f"Matches required level ({level_map.get(target_level)})." if max_candidate_level >= target_level else f"Partial match. Candidate has level {max_candidate_level} but requirement is {target_level}."
        
        # Weights: Degree Level (40%), Academic Performance (40%), Prestige (20%)
        # normalise prestige for the breakdown display
        prestige_component_score = 1.0 if prestige_bonus >= 0.2 else (0.5 if prestige_bonus > 0 else 0.2)
        
        # Breakdown
        breakdown.append({
            "component": "Degree Level Match",
            "score": level_score,
            "notes": note,
            "source_details": [
                {
                    "source": "Academic Audit",
                    "score": level_score,
                    "trust": 0.9,
                    "derivation": f"Match({level_map.get(max_candidate_level, 'None')}) vs Target({level_map.get(target_level, 'Bachelors')})",
                    "explanation": f"Candidate: {level_map.get(max_candidate_level, 'Unknown')} vs Requirement: {level_map.get(target_level, 'Bachelors')}"
                }
            ]
        })
        
        breakdown.append({
            "component": "Institutional Prestige",
            "score": prestige_component_score,
            "notes": f"Primary institution: {best_school} ({prestige_note}).",
            "source_details": [
                {
                    "source": "University Anchor",
                    "score": prestige_component_score,
                    "trust": 0.8,
                    "derivation": f"Tier Mapping: {prestige_note} (Bonus: {prestige_bonus:.2f})",
                    "explanation": f"Tier Rank: {prestige_note}"
                }
            ]
        })

        breakdown.append({
            "component": "Academic Performance",
            "score": grade_multiplier,
            "notes": f"Best identified grade: {grade_label}.",
            "source_details": [
                {
                    "source": "Grade Audit",
                    "score": grade_multiplier,
                    "trust": 0.7,
                    "derivation": f"Normalisation: {grade_label} (Multiplier: {grade_multiplier:.2f})",
                    "explanation": f"Classification: {grade_label}"
                }
            ]
        })

        final_score = (level_score * 0.4) + (grade_multiplier * 0.4) + (prestige_component_score * 0.2)
        tech_formula = f"({level_score:.2f} * 0.4) + ({grade_multiplier:.2f} * 0.4) + ({prestige_component_score:.2f} * 0.2) = {final_score:.2f}"
        
        improvements = []
        if level_score < 1.0:
            improvements.append({"text": f"Ensure the CV explicitly states a degree level of {level_map.get(target_level, 'Bachelors')} or higher.", "gain": 0.4 * (1.0 - level_score), "variables": ["DegreeLevel"]})
        if grade_multiplier < grade_cfg["FIRST_CLASS"]:
            improvements.append({"text": "Achieve or explicitly state a 1st Class (or equivalent high GPA) to maximise academic performance score.", "gain": 0.4 * (grade_cfg["FIRST_CLASS"] - grade_multiplier), "variables": ["GradeWeight"]})
        if prestige_component_score < 1.0:
            improvements.append({"text": "Graduating from a Tier 1 (Global Elite) institution provides the maximum prestige bonus.", "gain": 0.2 * (1.0 - prestige_component_score), "variables": ["PrestigeBonus"]})
        
        if not improvements:
            improvements.append({"text": "Maximum score achieved across all educational criteria.", "gain": 0.0, "variables": []})

        return {
            "score": round(final_score, 2),
            "calculation_formula": "(DegreeMatch * 0.4) + (GradeMatch * 0.4) + (Prestige * 0.2)",
            "technical_formula": tech_formula,
            "glossary": [
                {
                    "variable": "DegreeLevel",
                    "description": "How their highest degree compares to the job requirement.",
                    "impact": "Binary match. 1.0 if they meet it.",
                    "sensitivity": "Drops to 0.5 if they have a degree but it's below the target."
                },
                {
                    "variable": "GradeWeight",
                    "description": "Weighting based on their final classification (1st, 2:1, etc).",
                    "impact": f"Scales from {grade_cfg['FIRST_CLASS']}x for a 1st down to {grade_cfg['LOWER_SECOND']}x for a 2:2.",
                    "sensitivity": f"Defaults to {grade_cfg['DEFAULT']}x if I can't find a specific grade."
                },
                {
                    "variable": "PrestigeBonus",
                    "description": "Extra points for top-tier or Russell Group universities.",
                    "impact": f"Tier 1 (+{cfg['PRESTIGE_BONUS']['TIER_1']}), Tier 2 (+{cfg['PRESTIGE_BONUS']['TIER_2']}).",
                    "sensitivity": "Doesn't apply if the institution isn't in our prestige list."
                }
            ],
            "breakdown": breakdown,
            "sources_used": list(set(sources_used)),
            "improvements": improvements[:3]
        }
