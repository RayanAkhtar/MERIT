# Recruiter ground truth (Study 13 pilot)

**Panel:** $N=4$ — $R_1$, $R_2$ (recruiters), $P_1$, $P_2$ (Imperial MEng peers).  
**Roles:** 3 hold-outs (frontend, ML, DevOps).  
**Scale:** UI Likert **1 = essential**, **5 = optional**. TF-IDF mapped via `round(6 - suggested_weight)`.

## Files

| File | Content |
|------|---------|
| `panel.json` | Evaluator roster |
| `session_logs.json` | Ratings + notes (12 sessions = 4×3) |
| `recruiter_weights_summary.json` | Flat comparison table |
| `../job_descriptions/holdout_0{1,2,4}_*.json` | Consensus + per-rater weights |

## Regenerate

```bash
python populate_ground_truth.py
python run_study.py
```
