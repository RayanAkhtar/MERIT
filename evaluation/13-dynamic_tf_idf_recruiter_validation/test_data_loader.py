from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_JD_DIR = os.path.join(SCRIPT_DIR, "test_data", "job_descriptions")


def load_jds_from_dir(
    jd_dir: Optional[str] = None,
    *,
    require_ground_truth: bool = False,
) -> List[Dict[str, Any]]:
    root = jd_dir or DEFAULT_JD_DIR
    jds: List[Dict[str, Any]] = []
    for name in sorted(os.listdir(root)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(root, name)
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        if require_ground_truth and not _has_recruiter_weights(doc):
            continue
        jds.append(doc)
    return jds


def _has_recruiter_weights(doc: Dict[str, Any]) -> bool:
    metrics = doc.get("metrics") or {}
    for category in ("Languages", "Technologies", "Education"):
        block = metrics.get(category) or {}
        for item in block.get("value") or []:
            if item.get("recruiter_weight") is not None:
                return True
    return False
