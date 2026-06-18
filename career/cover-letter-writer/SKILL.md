---
name: cover-letter-writer
description: "Use when writing a cover letter for a job application — generates a personalized letter that highlights matching skills and addresses skill gaps."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [job-hunt, cover-letter, career, application]
    related_skills: [jd-resume-matcher, resume-tailor, job-hunt-pipeline]
---

# Cover Letter Writer

> Generate a personalized cover letter based on your resume and the job description. Highlights matching skills and frames missing skills as learning opportunities.

---

## When to Use

- *"Write a cover letter for this software engineer position"*
- *"Generate a personalized cover letter based on my resume and the JD"*
- *"帮我写一封求职信"*

---

## Output Template

```markdown
# Cover Letter — {Company}

**Role:** {Position}
**Date:** {YYYY-MM-DD}

---

Dear Hiring Manager,

I am writing to express my strong interest in the {Position} role at {Company}. 
With my experience in {top_skills}, I am confident I can contribute to your team.

**Why I'm a great fit:**
{2-3 sentences highlighting matched skills with concrete examples}

**Skills I bring:**
{list matching skills with brief context}

**What I'm excited to learn:**
{frame missing skills as growth opportunities}

I would welcome the opportunity to discuss how my background aligns with
{Company}'s needs. Thank you for your consideration.

Best regards,
{Your Name}
```

---

## Usage

```bash
hermes -s cover-letter-writer
"Write a cover letter for a Senior Software Engineer position 
 at Stripe. My resume is at ~/resume.txt, JD is at ~/stripe-jd.txt"
```
