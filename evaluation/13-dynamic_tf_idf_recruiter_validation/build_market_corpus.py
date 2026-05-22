"""
Study 13: Build a reproducible TF-IDF market corpus from local job-description PDFs.

Default source: MERIT/data/job descriptions/ (100 synthetic tech JDs).
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_JD_DIR = os.path.join(REPO_ROOT, "data", "job descriptions")
DEFAULT_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "corpus")

sys.path.insert(0, REPO_ROOT)
from backend.core.parsers.job_description import parse_jd  # noqa: E402

FILENAME_RE = re.compile(
    r"^(\d+)_(?P<seniority>intern|junior|mid|senior|lead|staff|principal|manager|director)_(?P<role>[a-z0-9\-]+)\.pdf$",
    re.IGNORECASE,
)


def parse_filename_meta(filename: str) -> Dict[str, str]:
    m = FILENAME_RE.match(filename)
    if not m:
        return {"doc_id": os.path.splitext(filename)[0], "seniority": "unknown", "role_slug": "unknown"}
    return {
        "doc_id": m.group(1),
        "seniority": m.group("seniority").lower(),
        "role_slug": m.group("role").lower().replace("-", " "),
    }


def collect_skill_terms(parsed: Dict[str, Any]) -> List[str]:
    terms: List[str] = []
    for key in ("technical_skills", "languages", "nice_to_have", "education_required"):
        val = parsed.get(key)
        if isinstance(val, list):
            terms.extend(str(v).strip() for v in val if v)
        elif isinstance(val, str) and val:
            terms.append(val.strip())
    return sorted(set(t for t in terms if t))


def build_corpus(jd_dir: str, output_dir: str) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)
    parsed_dir = os.path.join(output_dir, "parsed")
    os.makedirs(parsed_dir, exist_ok=True)

    pdf_files = sorted(f for f in os.listdir(jd_dir) if f.lower().endswith(".pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF job descriptions found in: {jd_dir}")

    documents: List[Dict[str, Any]] = []
    descriptions_only: List[str] = []
    failures: List[Dict[str, str]] = []
    skill_doc_freq: Counter = Counter()

    for filename in pdf_files:
        path = os.path.join(jd_dir, filename)
        meta = parse_filename_meta(filename)
        try:
            parsed = parse_jd(path)
            raw_text = (parsed.get("raw_text") or "").strip()
            if not raw_text:
                raise ValueError("empty raw_text after parse")

            skills = collect_skill_terms(parsed)
            word_count = len(re.findall(r"\w+", raw_text.lower()))

            doc = {
                **meta,
                "filename": filename,
                "source_path": os.path.relpath(path, REPO_ROOT).replace("\\", "/"),
                "job_title": parsed.get("job_title"),
                "company": parsed.get("company"),
                "word_count": word_count,
                "skill_count": len(skills),
                "skills": skills,
                "description": raw_text,
            }
            documents.append(doc)
            descriptions_only.append(raw_text)

            parsed_out = os.path.join(parsed_dir, filename.replace(".pdf", ".json"))
            with open(parsed_out, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2, ensure_ascii=False)

            for skill in skills:
                skill_doc_freq[skill.lower()] += 1

        except Exception as exc:
            failures.append({"filename": filename, "error": str(exc)})

    with open(os.path.join(output_dir, "corpus_documents.json"), "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, "corpus_descriptions.json"), "w", encoding="utf-8") as f:
        json.dump(descriptions_only, f, indent=2, ensure_ascii=False)

    with open(os.path.join(output_dir, "corpus_documents.jsonl"), "w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")

    with open(os.path.join(output_dir, "skill_document_frequency.csv"), "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["skill", "document_frequency", "corpus_size"])
        n_docs = len(documents)
        for skill, df in skill_doc_freq.most_common():
            writer.writerow([skill, df, n_docs])

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_directory": os.path.relpath(jd_dir, REPO_ROOT).replace("\\", "/"),
        "document_count": len(documents),
        "failed_count": len(failures),
        "unique_skills": len(skill_doc_freq),
        "seniority_distribution": dict(Counter(d["seniority"] for d in documents)),
    }

    with open(os.path.join(output_dir, "corpus_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    if failures:
        with open(os.path.join(output_dir, "parse_failures.json"), "w", encoding="utf-8") as f:
            json.dump(failures, f, indent=2, ensure_ascii=False)

    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jd-dir", default=DEFAULT_JD_DIR)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    manifest = build_corpus(os.path.abspath(args.jd_dir), os.path.abspath(args.output_dir))
    print(f"[SUCCESS] Parsed {manifest['document_count']} job descriptions.")


if __name__ == "__main__":
    main()
