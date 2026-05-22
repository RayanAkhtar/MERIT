# Study 13: Metric Prediction vs Recruiter Alignment (Pilot)

Validates **Pillar 1 metric prediction** (TF-IDF suggested priorities vs blinded human ratings).

## Scale

| Component | Size |
|-----------|------|
| Market corpus | 100 JDs (`data/job descriptions/`) — IDF only |
| Human study | **3 hold-outs**, **4 evaluators** (2 recruiters + 2 Imperial peers) |
| Skills rated | 27 total |

## Hold-outs (human study)

1. Junior Frontend (React)
2. Senior ML Engineer
3. Lead DevOps / Platform

## Commands

```bash
python build_market_corpus.py
python build_test_dataset.py
python populate_ground_truth.py
python run_study.py
```

## Report

`FYP-report/evaluation/subsections/foundational_accuracy.tex` (Study 13)

## Historical record

`response.txt` — plain-language facilitator notes and results summary from the pilot run.
