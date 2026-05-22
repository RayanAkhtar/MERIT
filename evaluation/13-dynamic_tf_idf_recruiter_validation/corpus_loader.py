from __future__ import annotations

import json
import os
from typing import List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CORPUS_PATH = os.path.join(SCRIPT_DIR, "corpus", "corpus_descriptions.json")


def load_corpus_descriptions(path: str | None = None) -> List[str]:
    corpus_path = path or DEFAULT_CORPUS_PATH
    with open(corpus_path, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {corpus_path}")
    return [str(d) for d in data if d]
