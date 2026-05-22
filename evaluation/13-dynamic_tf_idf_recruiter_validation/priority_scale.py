"""
Priority scales in MERIT:

- Backend TF-IDF ``suggested_weight``: 1.0 (low significance on this JD) → 5.0 (high).
- UI / recruiter Likert (ConfigEditor): **1 = highest priority**, **5 = lowest**.

Study 13 compares human ratings in UI convention to TF-IDF mapped into the same convention
(``6 - round(suggested_weight)``, matching ``ConfigEditor.tsx``).
"""

from __future__ import annotations


def tfidf_continuous_to_ui_priority(weight: float) -> int:
    """Map backend suggested_weight to UI priority 1--5 (1 = must-have)."""
    return max(1, min(5, int(round(6 - weight))))


# Legacy name kept for imports; do NOT use for Study 13 evaluation.
def continuous_to_likert(weight: float) -> int:
    return tfidf_continuous_to_ui_priority(weight)
