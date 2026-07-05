---
name: linkedin-post-generator
description: "Use when creating LinkedIn posts — long-form thought leadership, hook-driven, optimized for the LinkedIn algorithm (3000 char limit, line-break density, native formats)."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [linkedin, social-media, thought-leadership, content-creation, professional]
    related_skills: [twitter-thread-writer, content-repurposer, xiaohongshu-post-writer, newsletter-digest]
---

# LinkedIn Post Generator

> Turn ideas, articles, lessons, or experiences into optimized LinkedIn posts. Hook-driven, scannable, ≤3000 chars, structured for the LinkedIn algorithm (line breaks, short paragraphs, native formats).

LinkedIn is **not** Twitter, **not** 小红书, **not** a blog. It rewards:

- **The first 2 lines** (above the "see more" fold)
- **Short lines, lots of white space** (mobile-first)
- **Hook → Story → Insight → CTA** structure
- **Dwell time** (people reading, not scrolling past)
- **Comments in the first 60 minutes** (early engagement compounds)

This skill enforces all of the above with measurable rules.

---

## Overview

| Capability | Description |
|------------|-------------|
| **Hook Crafting** | First 2 lines optimized for the "see more" fold; curiosity, contrarian, or pain-driven |
| **Structure Selection** | Choose from 6 proven formats (Story, List, Contrarian, How-To, Frame, Data) |
| **Length Discipline** | Strict ≤3000 char limit, recommended 1300–1800 for engagement sweet spot |
| **Line-Break Density** | Max 1 sentence per line; average line length ≤80 chars |
| **CTA Engineering** | End with a question that invites debate, not "like and share" begging |
| **Hashtag Strategy** | 3–5 niche-specific hashtags placed at the bottom, not inline |
| **Engagement Prediction** | Score the draft against 5 algorithm signals before publishing |

---

## When to Use

- *"Write a LinkedIn post about my product launch"*
- *"Turn this article into a LinkedIn post"*
- *"Help me share what I learned from this book on LinkedIn"*
- *"Write a thought leadership post about AI in healthcare"*
- *"Draft a LinkedIn post celebrating my team's promotion"*
- *"Repurpose this Twitter thread into a LinkedIn post"*
- *"给我写一篇中文 LinkedIn 帖子"*

---

## Core Workflow

### Step 1: Identify the Post Format

Choose ONE structure. Each format has a specific rhythm.

| Format | When to Use | Rhythm |
|--------|-------------|--------|
| **Personal Story** | Lessons learned, career moments, failures | Hook → Setup → Conflict → Resolution → Insight |
| **Listicle** | "5 lessons", "3 mistakes", tactical tips | Hook → Numbered items (one per line) → Twist → CTA |
| **Contrarian Take** | Going against popular opinion | Hook (bold claim) → Why most are wrong → Your evidence → "But here's the nuance" |
| **How-To / Framework** | Teaching a process | Hook (problem) → Step 1 → Step 2 → Step 3 → Common mistake → CTA |
| **Observation / Trend** | Industry insight, data commentary | Hook (what you noticed) → Context → 3 implications → What it means for you |
| **Celebration / Milestone** | Promotions, launches, anniversaries | Hook (gratitude or surprise) → Story → What made it work → Thank yous |

Ask the user (or infer): *"What did you learn / build / notice / change your mind about?"* — this decides the format.

---

### Step 2: Craft the Hook (Most Important Step)

The first **2 lines** are everything. Above the fold, they decide if the reader clicks "see more" or scrolls past.

**7 proven hook patterns:**

1. **The Result Hook** — *"I made $50K in 30 days doing X. Here's the playbook."*
2. **The Mistake Hook** — *"I wasted 3 years building the wrong thing. Here's what I wish I knew."*
3. **The Question Hook** — *"Why do smart people make dumb career decisions?"*
4. **The Contrarian Hook** — *"Working 80 hours a week is the worst advice in startup history."*
5. **The Pattern Hook** — *"After 100 customer interviews, I noticed 3 things nobody talks about."*
6. **The Vulnerability Hook** — *"I got fired last Tuesday. Here's the email I sent my team."*
7. **The List Hook** — *"5 things I wish someone told me before I became a manager."*

**Hook Rules:**

- **Never** start with "I'm excited to announce…" or "Today I learned…"
- **Never** start with a generic statement ("In today's fast-paced world…")
- The hook should create **curiosity gap** OR **promise value** OR **trigger emotion** (anger, surprise, recognition)
- First line ≤120 chars (so the entire line shows above the fold on mobile)

---

### Step 3: Build the Body with White Space

LinkedIn is a **mobile-first, scrolling platform**. Walls of text get skipped.

**Mandatory formatting rules:**

```
✓ One sentence per line (or one short phrase)
✓ Blank line between every sentence
✓ No paragraphs longer than 3 lines
✓ Use emoji sparingly (0-3 per post, never as bullet points)
✓ Bold via CAPS or ➤ arrows if needed
✓ Numbers, lists, and structure break up text
✗ NO walls of text
✗ NO hashtags inside the body
✗ NO "Like and share if you agree!"
```

**Example of correctly formatted body:**

```
Last year, I almost quit engineering.

Not because the work was hard.
Because nobody told me the rules.

Here's what I learned the hard way:

1. Your manager is not your career plan.
   You are. Write your own roadmap.

2. "Promoting" doesn't mean "good at job."
   It means "good at job + leading others."

3. The best engineers I know say no 80% of the time.
   Focus is the real superpower.

4. Nobody cares about your tech stack.
   They care about the problem you solved.

5. Your network compounds.
   Every conversation is a future opportunity.

The biggest lesson?
```

---

### Step 4: Write a Real CTA (Not a Begging One)

Bad CTAs:
- *"Like and share if you found this useful!"* (begging, ignored)
- *"Follow me for more content!"* (transactional, off-putting)

Good CTAs (invite **debate** or **specific response**):

```
→ "What's the worst career advice you've ever received?"
→ "Am I wrong here? Tell me in the comments."
→ "Which of these 5 resonates most with you?"
→ "What's the #1 thing you wish you knew 5 years ago?"
→ "If you've felt this, I want to hear your story."
```

The CTA should be **specific** enough that the answer can't be a one-word "yes."

---

### Step 5: Add Hashtags (Bottom Only)

- **3–5 hashtags**, placed at the very bottom on their own lines
- Mix: **1 broad** (`#leadership`) + **2 niche** (`#engineeringmanagement`) + **1 trending** (`#futureofwork`) + **1 personal brand** (optional)
- Don't put hashtags in the body — they're visual clutter

Example:
```
#leadership #engineeringmanagement #careergrowth
```

---

### Step 6: Verify with Algorithm Score

Before delivery, score the post on 5 signals:

```python
def linkedin_score(post):
    score = 0
    issues = []

    # 1. Hook strength (first 2 lines)
    hook = '\n'.join(post.split('\n')[:2])
    if len(hook) > 240:
        issues.append("Hook too long — first 2 lines exceed 240 chars (gets cut off)")
    if any(hook.lower().startswith(bad) for bad in ['i am excited', "i'm excited", 'today i learned', 'in today']):
        issues.append("Generic hook — replace with curiosity or contrarian opener")
    else:
        score += 20

    # 2. Total length
    total = len(post)
    if total > 3000:
        issues.append(f"Exceeds 3000 chars ({total}) — LinkedIn will truncate")
    elif 1300 <= total <= 1800:
        score += 25  # Sweet spot
    elif total < 800:
        issues.append("Too short — LinkedIn rewards 1300–1800 char posts")

    # 3. Line break density (white space)
    lines = [l for l in post.split('\n') if l.strip()]
    long_lines = [l for l in lines if len(l) > 200]
    if len(long_lines) > 2:
        issues.append(f"{len(long_lines)} lines exceed 200 chars — break them up")
    else:
        score += 20

    # 4. CTA quality
    if any(bad in post.lower() for bad in ['like and share', 'follow me', 'repost if']):
        issues.append("Begging CTA — replace with a question that invites debate")
    elif '?' in post.split('\n')[-3:][0]:  # question near the end
        score += 20

    # 5. Hashtag strategy
    hashtag_count = sum(1 for line in post.split('\n') if line.strip().startswith('#') and not line.startswith('#!'))
    if 3 <= hashtag_count <= 5:
        score += 15
    elif hashtag_count > 5:
        issues.append("Too many hashtags — keep 3–5")

    return score, issues
```

**Score interpretation:**

- **80–100:** Ready to publish, high engagement potential
- **60–79:** Good, fix 1-2 minor issues
- **40–59:** Needs significant rework (weak hook or wrong structure)
- **<40:** Rewrite from scratch

---

### Step 7: Deliver with Engagement Tips

Always include alongside the post:

1. **Best posting time** for the user's timezone (default: Tue–Thu, 8–10am local)
2. **First 60 minutes strategy** — *"Reply to every comment in the first hour. The algorithm tracks this."*
3. **Suggested comment seed** — *"Post your own comment in the first 5 minutes to start the thread."*
4. **A/B hook variation** — Give 1 alternate hook for testing

---

## Example Invocations

### Example 1: Personal Story Post

```
User: "Help me write a LinkedIn post about getting rejected from Y Combinator"

Hermes should:
  1. Identify format: Personal Story / Vulnerability Hook
  2. Craft hook: "YC rejected us last week. Here's the email that made me cry in a Starbucks."
  3. Build body with white space:
     - The setup (we applied, we thought we had it)
     - The rejection (the email, the moment)
     - What I learned (3 specific takeaways)
     - What's next (rebuilding, applying again)
  4. CTA: "Have you ever been rejected by something you really wanted? What did you do next?"
  5. Hashtags: #startups #yc #rejection #founderlife
  6. Score: verify hook strength, length (1300-1800), white space density
  7. Deliver with first-60-minutes engagement strategy
```

### Example 2: Repurposing a Twitter Thread

```
User: "Turn this Twitter thread about debugging into a LinkedIn post"

Hermes should:
  1. Read the Twitter thread (10 tweets, ~280 chars each)
  2. Compress from 10 tweets → 1 LinkedIn post (1500 chars)
  3. Replace 🧵 numbering with numbered list (1, 2, 3…)
  4. Convert casual Twitter tone → slightly more professional (still human)
  5. Add a personal story wrapper ("Last month I spent 8 hours debugging…")
  6. End with a debate CTA: "What's the longest you've ever spent on one bug?"
  7. Strip Twitter-specific elements (no 🧵, no 1/10)
  8. Add niche hashtags at the bottom
```

### Example 3: Thought Leadership on Industry Trend

```
User: "Write a LinkedIn post about why I think AI will replace junior developers in 3 years"

Hermes should:
  1. Identify format: Contrarian Take (or mainstream-but-strong opinion)
  2. Hook: "Junior dev roles will disappear by 2028. Here's why I'm not worried."
  3. Body structure:
     - The trend (data: job postings down 30% YoY at entry level)
     - Why most are wrong (it's not replacement, it's evolution)
     - What will actually happen (junior → AI-augmented roles)
     - What seniors should do (focus on judgment, not typing)
     - What juniors should do (learn to direct AI, not compete with it)
  4. CTA: "Am I being too optimistic? Too pessimistic? Where's your take?"
  5. Hashtags: #ai #softwareengineering #futureofwork #juniordev
  6. Add engagement strategy: "Reply to early comments, especially the disagreeing ones — controversy drives reach."
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Wall of text** (paragraphs >3 lines) | Break every sentence onto its own line; blank line between ideas |
| **Generic hook** ("In today's fast-paced world…") | Use one of the 7 hook patterns; first line must create curiosity or promise value |
| **Begging CTA** ("Like and share if you agree") | Replace with a specific question that demands a real answer |
| **Too many hashtags** (10+ inline) | Cap at 3–5, place at the bottom on separate lines |
| **Wrong format** (using a Story structure for tactical tips) | Match the format to the content: tactical = Listicle, lesson = Story, opinion = Contrarian |
| **Too short** (<800 chars) | Expand with examples, specifics, numbers — LinkedIn rewards depth |
| **Too long** (>3000 chars) | Cut the weakest section, merge redundant points |
| **Corporate tone** ("We are pleased to announce…") | Write in first person, use contractions, sound like a human |
| **No personal stake** | Every great LinkedIn post has a "why I care" element; add yours |
| **Posting at wrong time** | Default to Tue–Thu 8–10am local; warn the user if they say "I want to post now" at a low-engagement time |

---

## Verification Checklist

- [ ] Hook is ≤120 chars on first line, ≤240 chars across first 2 lines
- [ ] Hook uses one of the 7 proven patterns (not a generic opener)
- [ ] Body uses one-sentence-per-line formatting with blank lines between
- [ ] Total post length is 1300–1800 chars (sweet spot) or ≤3000 (hard limit)
- [ ] No paragraphs exceed 3 consecutive lines
- [ ] No "wall of text" — average line length ≤80 chars
- [ ] CTA is a specific question that invites debate, not a begging statement
- [ ] Hashtags are 3–5 total, placed only at the bottom on their own lines
- [ ] No hashtags inline within the body text
- [ ] Format matches the content (Story / List / Contrarian / How-To / Observation / Celebration)
- [ ] Algorithm score ≥80
- [ ] No generic corporate phrases ("We are excited to announce")
- [ ] Personal stake or "why I care" element is present
- [ ] Engagement strategy provided (best time, first-60-min reply plan, comment seed)

---

## Data Sources & Accuracy

This skill uses **content heuristics**, not external APIs. All rules are derived from publicly discussed LinkedIn algorithm signals:

- **3000 character limit** — LinkedIn's official post limit
- **"See more" fold** — LinkedIn truncates posts after ~210 chars on mobile, ~140 on desktop; the hook must fit in ~240 chars to maximize fold visibility
- **Line break density** — Correlates with dwell time (LinkedIn rewards posts that get read, not scrolled past)
- **1300–1800 char sweet spot** — Based on aggregated engagement data from 2023–2025 LinkedIn creator studies
- **First 60 minutes engagement** — LinkedIn's algorithm tests posts on a small audience first; high early engagement expands reach exponentially
- **Hashtag count** — LinkedIn has officially moved away from recommending >5 hashtags; 3–5 is current best practice

Accuracy caveats:

- The algorithm evolves; specific character thresholds may shift, but the structural principles (hook strength, white space, debate CTA) remain stable
- A/B test your own posts to refine — this skill provides the framework, your audience calibrates the specifics