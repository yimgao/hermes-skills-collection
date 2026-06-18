---
name: job-hunt-pipeline
description: "Use when applying for jobs — runs the full pipeline: match resume vs JD → tailor resume → write cover letter → track application. One command does it all."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [job-hunt, pipeline, career, automation, application]
    related_skills: [jd-resume-matcher, resume-tailor, cover-letter-writer, job-tracker]
---

# Job Hunt Pipeline

> Full job application automation pipeline. Run once with your resume file and a JD — it will match, tailor, write a cover letter, and track the application.

---

## Pipeline Flow

```
resume.txt + jd.txt
       │
       ▼
┌──────────────────┐
│ jd-resume-matcher │ → match score, skill gaps, suggestions
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│ resume-tailor │ → tailored resume with missing skills filled
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ cover-letter-writer  │ → personalized cover letter
└──────┬──────────────┘
       │
       ▼
┌────────────┐
│ job-tracker │ → application recorded + follow-up reminder
└────────────┘
```

## Output

After running, you get:
- `resume-tailored.md` — customized resume
- `cover-letter.md` — personalized cover letter
- `data/applications.csv` — updated tracking
- Match score + skill gap report

---

## Usage

```bash
# Full pipeline
hermes -s job-hunt-pipeline
"I'm applying to a Senior Software Engineer role at Stripe. 
 My resume is at ~/resume.txt. Here's the JD: ..."
```

Or step by step:
```bash
cd ~/dev/job-hunt-tool
source .venv/bin/activate

# 1. Match
python3 -m src match -r resume.txt -j jd.txt

# 2. Tailor
python3 -m src tailor resume.txt jd.txt

# 3. Track
python3 -m src track --company Stripe --role "Senior Engineer"
```
