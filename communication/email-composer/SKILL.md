---
name: email-composer
description: "Use when drafting professional emails — generates business, job application, client, or customer emails based on context, tone, and key points."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [email, communication, professional, business, draft]
    related_skills: [interview-coach, presentation-helper, business-plan-generator]
---

# Email Composer

> Draft professional emails. Generates business, job application, client outreach, or customer service emails based on context, tone, and key points.

---

## When to Use

- *"Draft a cold email to a potential investor"*
- *"Write a follow-up email after my interview"*
- *"Compose a professional email to a client about a delayed project"*
- *"帮我写一封商务邮件"*

---

## Core Workflow

### Step 1: Gather Context

| Parameter | Example |
|-----------|---------|
| Type | Cold outreach, Follow-up, Customer, Internal, Apology |
| Recipient | Investor, Client, Boss, Team, Customer |
| Tone | Professional, Warm, Urgent, Apologetic |
| Key points | 3-5 things to convey |
| Call to action | What should recipient do? |

### Step 2: Generate Email

```markdown
**Subject:** {clear, action-oriented subject line}

**Body:**
{Greeting},

{Opening — context + who you are}

{Body — key points in 2-3 short paragraphs}

{Call to action — specific ask with timeline}

{Closing},
{Your name}
{Title / Company}
{Contact info}
```

### Step 3: Email Templates

**Cold outreach to investor:**
```
Subject: {1-line pitch} — seeking {amount}

Hi {Name},

I'm the founder of {company}. We're building {one-liner}.

In the last {timeframe}, we've achieved {key metrics}. 
We're raising a {round} round of ${amount}.

Would you be open to a 15-min call next week?

Best,
{Name}
```

**Job application follow-up:**
```
Subject: Follow-up — {Role} at {Company}

Hi {Name},

I wanted to follow up on my application for the {Role} 
position. I'm very excited about {specific thing about company}.

I'd love the opportunity to discuss how my experience in 
{skill} could contribute to {team/project}.

Looking forward to hearing from you!

Best,
{Name}
```

---

## Example

```
User: Draft a cold email to a venture capital firm about my ramen shop concept
Hermes should:
  1. Generate subject line: "Ramen + Gyoza concept — seeking $300K seed"
  2. Write 3-paragraph body: intro, traction/plan, ask
  3. Include clear CTA: "15-min call next week"
  4. Professional tone
```
