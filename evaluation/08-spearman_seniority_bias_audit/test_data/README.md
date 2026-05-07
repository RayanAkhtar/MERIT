# Spearman Correlation: Scenario B (Close Competition)

## Dataset Purpose
This dataset is designed to evaluate MERIT's "Glass-Box" intelligence when dealing with a highly competitive pool of candidates who all share the same primary skillset.

### Job Description
* **Role:** Intern Backend Engineer
* **Source File:** `job_description.pdf` (derived from `001_intern_backend-engineer.pdf`)

### Candidate Breakdown
The pool contains **10 candidates** who are all qualified for Backend or Software Engineering roles:
1. Aaron Mohammed (Mid-Level Backend Engineer)
2. Yusuf Nilsson (Junior Backend Engineer)
3. Moinecha Ramos-Horta (Mid-Level Backend Engineer)
4. Riko AlTayer (Senior Backend Engineer)
5. Iris Thijs (Staff Backend Engineer)
6. Patricia Al-Bahar (Principal Backend Engineer)
7. Eva Sderberg (Staff Backend Engineer)
8. Vincent Germain (Intern Backend Engineer)
9. Arif Cheng (Mid-Level Backend Engineer)
10. Milton Uati (Junior Software Engineer)

## Why this is a good test
This scenario audits the "Seniority Bias" common in automated systems. While a human recruiter for an **Intern** role would prioritize entry-level candidates (Vincent, Yusuf, Milton) and filter out overqualified Seniors, many ATS engines default to ranking the most experienced candidates at the top. This study quantifies that tension using Spearman's Rho.
