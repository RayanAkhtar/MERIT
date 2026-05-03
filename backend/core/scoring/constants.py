# scoring configuration constants
# these numbers impact the match % calculations directly.
# mostly initial guesses for now, might need to tweak them after testing more candidates

SCORING_CONSTANTS = {
    "LANGUAGES": {
        "GH_VERIFICATION_THRESHOLD": 50.0,  # LoC % required for 100% score on the github side
        "CV_PROMINENCE_PENALTY": 0.8,       # 20% penalty if not the primary skill
        "CONSENSUS_MULTIPLIER": 1.15,      # Multiplier if found on both CV and GitHub
        "RECENCY": {
            "DECAY_LAMBDA": 0.12,          # lambda for exponential decay: e^(-lambda * years)
            "ACTIVE_THRESHOLD": 1.0,       # years before decay starts hitting hard
            "BOOST_ACTIVE": 1.05           # slight bonus for current skills
        }
    },
    "EDUCATION": {
        "PRESTIGE_BONUS": {
            "TIER_1": 0.20,                # Oxford, Cambridge, Imperial, LSE, UCL (top tier)
            "TIER_2": 0.10,                # Warwick, Durham, Edinburgh, etc.
            "TIER_3": 0.05                 # russell group
        },
        "GRADE_MULTIPLIER": {
            "FIRST_CLASS": 1.0,            # 1st / 4.0 GPA
            "UPPER_SECOND": 0.9,           # 2:1
            "LOWER_SECOND": 0.7,           # 2:2
            "DEFAULT": 0.85                # Assumed 2:1
        },
        "MATCH_WEIGHTS": {
            "DEGREE_LEVEL": 0.8,
            "INSTITUTION": 0.2
        }
    },
    "PROFESSIONAL_GRAVITY": {
        "TENURE_MAX_YEARS": 5.0,           # Normalised against 5 years
        "LOYALTY_THRESHOLD": 2.0,          # Years at one company for loyalty bonus
        "LOYALTY_BONUS": 0.15,
        "IMPACT_DENSITY_WEIGHT": 0.25
    },
    "TECH_STACK": {
        "LI_BASE_SCORE": 0.70,
        "CV_BASE_SCORE": 0.50,
        "CONSENSUS_MULTIPLIER": 1.15,
    },
    "ANTI_STUFFING": {
        "OCCURRENCE_LIMIT": 5,             # max times a keyword can appear (in the cv) before penalty to avoid keyword stuffing
        "PENALTY_PER_OCCURRENCE": 0.03,    # Score reduction for each occurrence over limit
        "MAX_TOTAL_PENALTY": 0.30          # Cap the penalty at 30% of score for that metric (no reason for them to mention that many times)
    },
    "FUSION": {
        "SOURCE_CONFIDENCE": {
            "TECHNICAL_SKILLS": {
                "GITHUB": 0.90,     # Direct work sample evidence
                "CV": 0.70,         # Self reported
                "LINKEDIN": 0.30,   # Low trust for specific language skills
                "RECENCY": 0.85     # Temporal analysis confidence
            },
            "PROFESSIONAL_HISTORY": {
                "CV": 0.9,         # Primary source for role dates
                "LINKEDIN": 0.50    # Strong public verification for tenure, lower score since linkedin experience is less focused to the job role
            }
        },
        "THRESHOLDS": {
            "HIGH": 0.15,       # std_dev below this is High Confidence
            "MEDIUM": 0.25      # std_dev below this is Medium Confidence
        },
        "PRIORS": {
            "ALPHA": 1.0,
            "BETA": 1.0
        }
    }
}
