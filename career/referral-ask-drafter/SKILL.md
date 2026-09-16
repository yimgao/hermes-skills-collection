---
name: referral-ask-drafter
description: "Get warm intros at target companies without sounding transactional. Generates referrer-researched, channel-aware (LinkedIn DM / email / WhatsApp / WeChat / text / in-person) referral-ask messages, follow-up sequences, and yes/no/graceful-no branching. Tracks who you asked, response rate, and which warm intros converted to interviews. Pairs with job-hunt-pipeline (apply step), personal-crm (relationship history), and salary-negotiation-coach (after the offer)."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [career, networking, referral, warm-intro, linkedin, cold-message, followup, job-search, job-hunt, weak-ties, alumni-network, wechat, professional-network]
    related_skills: [job-hunt-pipeline, job-tracker, personal-crm, salary-negotiation-coach, cover-letter-writer, jd-resume-matcher, meeting-prep-brief]
---

# 🤝 Referral Ask Drafter — Warm Intro 邮件/私信教练

> Referrals are still the single highest-leverage move in any job search — most hiring managers read referred resumes first, and referred candidates are 4–5× more likely to be hired than cold applicants. But almost no one writes a good referral-ask message: they over-explain, sound needy, apologize for asking, or paste a generic template that screams "I copied this from Google." This skill turns "I want to work at Stripe" into a researched, channel-appropriate, low-friction message to the one or two people in your network who can actually help — plus a follow-up sequence, a graceful-no path, and a tracker that shows your conversion rate by message type.
>
> 内推依然是求职中性价比最高的一步——大多数招聘经理会优先看内推简历，内推候选人被录用的概率比海投高 4–5 倍。但几乎没人能写好一封内推请求：要么过度解释，要么显得卑微，要么直接复制模板让人一眼看穿。这个 skill 帮你从人脉里精准挑出能帮上忙的 1–2 个人，按渠道（领英/邮件/微信/短信/面对面）生成得体不别扭的请求，加上一组后续跟进、一条礼貌退路，以及一张转化率追踪表。

## Overview / 概述

Referral Ask Drafter is a **networking-psychology + message-crafting + conversion-tracking** coach for the most-avoided moment in any job search: reaching out to someone you haven't talked to in 1–3 years and asking them to put their name behind your application. The premise: most professionals have **200–600 weak ties** (former classmates, ex-colleagues, conference contacts, online mutuals) but only reach out to 3–5 of them per search. The reason isn't laziness — it's **fear of looking needy, awkward, or transactional**, plus the genuine uncertainty about whether the relationship is "warm enough" to ask.

This skill solves that by:

1. **Picking the right person** — shortlist 1–3 highest-leverage referrers from your network (or a network you don't have yet, with strategies to find them)
2. **Researching them in 60 seconds** — pull their current role, tenure, recent posts, mutual context, and the *exact* way to make the ask feel easy and natural
3. **Drafting a channel-appropriate message** — LinkedIn DM, email, WeChat, WhatsApp, SMS, or face-to-face script; each with a different length, tone, and CTA
4. **Providing a follow-up cadence** — 7-day, 14-day, and 21-day touchpoints that don't feel pushy
5. **Handling yes / no / silence** — branched scripts for "happy to refer," "can't refer but here's a tip," and the awkward 30-day silence
6. **Tracking conversion** — local ledger of every ask, response rate, intro success rate, and which message styles convert

All scripts are **adaptive to your relationship depth** (cold-weak-tie vs. former-manager vs. acquaintance), **local-first** (no LinkedIn automation, no scraping, no fake-account hacks), and **Chinese/English bilingual** with culture-aware phrasing.

| Capability | What It Does | How |
|------------|-------------|-----|
| **Network triage** | From your contacts (or a target-company-only list), pick the 1–3 highest-leverage people to ask | Heuristic: company match + recency + warmth + role proximity |
| **Relationship-depth calibration** | Decide whether this is a cold-weak-tie, acquaintance, ex-colleague, or former-manager ask | 4-tier rubric with different ask templates per tier |
| **Referrer research pack** | 60-second dossier: current role, time-in-role, recent LinkedIn activity, mutual context, "give them an easy out" hook | Chat-based intake + paste-friendly profile digest |
| **Channel-aware drafting** | LinkedIn DM (≤300 chars), email (≤200 words), WeChat/WhatsApp/SMS (≤80 chars hook + offer to switch), face-to-face script | 5 channel templates, each tone-matched |
| **The "easy ask" framing** | Make the request feel low-effort: provide resume link, JD link, target team, suggested 2-line forward blurb | Forward-blurb generator |
| **Follow-up cadence** | Day 7 (gentle bump), Day 14 (different angle), Day 21 (graceful close) | Auto-drafted per stage |
| **Branched scripts for outcomes** | Yes → thank-you + keep loop warm; No-refer-but-tip → pivot gracefully; Silent → stop at 21 days | 3 outcome templates |
| **Cold-weak-tie acquisition** | No 1st-degree contacts at target? 4 strategies: alumni, open LinkedIn posts, conference mutuals, "warm" 2nd-degree intros | Strategy playbook |
| **Conversion tracker** | Local JSON: per-ask — date, target, referrer, channel, response time, outcome, converted-to-interview | `~/.hermes/data/referrals/ledger.json` |
| **Bilingual scripts** | US English + 中文 templates with culture-aware phrasing (领英 vs 微信 vs 脉脉 vs email) | Channel- + culture-specific |
| **Cron-friendly reminder** | Set a cron to nudge you 14 days after any "no response yet" — never miss a warm intro | `hermes cron` |

## When to Use

- *"I want to work at Stripe — who in my network could refer me, and what do I actually say?"*
- *"I haven't talked to my ex-colleague Maya in 2 years — is it weird to ask her for a referral to Notion?"*
- *"I have 3 target companies and almost no warm intros. How do I build them in 2 weeks?"*
- *"Someone said 'happy to refer — what should I send them?' — draft the email to make their job easy."*
- *"I asked my manager from 4 years ago for a referral and she left me on read. Follow up or give up?"*
- *"Draft a LinkedIn DM to a VP at OpenAI whose post I commented on last week."*
- *"帮我写一条微信给我前同事，问能不能帮我内推字节。"*
- *"我想投一家 FAANG，但国内人脉没有 1st-degree connection，怎么破？"*
- *"My referrer said yes — write the email so they can forward my resume to the hiring manager in 30 seconds."*
- *"I want to ask for a referral without sounding like I'm using the relationship."*
- *"What's the right follow-up if they don't reply in a week?"*
- *"Set a cron to remind me about 3 pending referrals I haven't heard back on."*
- Any mention of **"referral", "内推", "warm intro", "ask my network", "weak ties", "who do I know at", "old colleague", "former coworker", "alumni", "LinkedIn DM", "wechat ask", "内推信"**

**Do NOT use** for: cold-applying without a referrer (use `job-hunt-pipeline`), resume/cover-letter content (use `cover-letter-writer` / `jd-resume-matcher`), salary/offer negotiation (use `salary-negotiation-coach`), recruiter outreach at staffing agencies (different play — agency recruiters don't need referral scripts), or sales cold outreach (different skill entirely).

## Core Workflow

### Step 1: Define the Ask

**Inputs needed** (ask the user via 5 quick questions or pull from `job-hunt-pipeline` context):

1. **Target company** — e.g. *"Stripe"* (1 primary; optional 2nd/3rd stretch goal)
2. **Target role / team** — e.g. *"Senior Backend Engineer, Payments Platform"* or *"PM, Growth"*
3. **JD link** (optional but very helpful — enables forward-blurb generation)
4. **Resume link** (LinkedIn / personal site / PDF URL — never paste full resume in the DM)
5. **What you can offer back** — informational interview? Coffee chat? A relevant intro? Reciprocal help? (Most people skip this and lose the ask.)

**Output of Step 1:** a clean Ask Brief:

```markdown
## Ask Brief
- **Target:** Stripe · Senior Backend Engineer · Payments Platform
- **JD:** https://stripe.com/jobs/... (captured key requirements)
- **Resume:** https://linkedin.com/in/you
- **Reciprocal offer:** "Happy to buy you coffee / give you a 20-min PM-to-PM chat on B2B SaaS onboarding" (or whatever's real)
```

### Step 2: Pick the Referrer(s)

From the user's network, generate a ranked shortlist using this heuristic:

| Factor | Weight | Why |
|--------|--------|-----|
| Currently at target company | **×3** | Only they can submit a referral in most ATS workflows |
| Time in role 6+ months | **×1.5** | New hires usually can't refer yet; old hires have more pull |
| Relationship warmth (worked together > acquaintance > cold) | **×2** | Strong ties convert 5× more than weak ties |
| Same function as you (eng-to-eng, PM-to-PM) | **×1.5** | They speak your language and can sell your skillset |
| Recent interaction (<90 days) | **×1.5** | A like/comment last quarter is warmer than a stale 2-year connection |
| Hiring manager or above | **+1 tier** | A skip-level intro > peer intro |

**Top output:** 3 ranked names + a "stretch" name if no 1st-degree exists.

**If the user has zero 1st-degree contacts at the target**, switch to **Step 2-Cold** (acquisition playbook below).

**For each name, generate a 60-second dossier:**

```markdown
### Maya Patel (recommendation tier: STRONG)
- **Role:** Engineering Manager · Payments Platform · at Stripe since 2021
- **Mutual context:** Worked together at Acme Co. 2020–2022, same team
- **Recent signal:** Posted on LinkedIn 9 days ago about hiring "strong backend engineers for Payments" ← DIRECT HOOK
- **Warmth score:** 8/10 (former teammate, last contact 14 months ago — she's liked 2 of your posts since)
- **Easy-out hook:** You know she referred another ex-Acme colleague in 2024 (low effort precedent)
- **Suggested ask frame:** "Saw your post about hiring — congratulations on the team's growth. Two questions, one easy, one bigger…"
```

### Step 3: Choose the Channel & Draft the Message

Ask the user (or default to the highest-conversion channel they have with this referrer):

| Channel | Best for | Length limit | Tone |
|---------|----------|--------------|------|
| **LinkedIn DM** | Weak ties, ex-colleagues you haven't emailed in years | ≤300 chars first message | Polished, professional |
| **Email** | Ex-managers, ex-colleagues you actually have an address for | ≤200 words | Slightly warmer |
| **WeChat / WhatsApp / iMessage** | Close former colleagues, alumni you message casually | ≤80 chars hook + bridge to longer | Casual, brief |
| **SMS / Text** | Very-close former colleagues only | ≤160 chars | Personal, fast |
| **In-person / Zoom ask** | Current colleagues, friends, alumni at events | Live script (no written) | Conversational |

**Drafting rules** (apply to all channels):

1. **Subject line / hook**: Specific to *them*, not to you. *"Saw your hiring post — congrats"* beats *"Quick question about a job"* beats *"Resume attached"*
2. **First sentence**: Recall a specific shared context. *"We worked on the 2021 migration together"* not *"We've met before"*
3. **The ask itself**: 1 sentence, specific role + company + link. *"I'm applying to the Senior Backend role on Payments Platform (link) and wondering if you'd be open to a quick internal referral."*
4. **Make their job easy**: Offer the forward blurb + JD link + your resume link. **Most ask-ers skip this and lose.**
5. **The graceful out**: *"Totally fine if no — happy to grab coffee next time I'm in SF either way."* This is what makes the ask feel low-pressure.
6. **No emojis in professional channels**. LinkedIn DM: zero. WeChat: 1 max if you usually use them.
7. **Length**: 1st LinkedIn message = ≤300 chars; if they reply, expand. Email = ≤200 words, ≤5 short paragraphs.

**Examples (each is ready to copy-paste with name/role filled in):**

#### LinkedIn DM — ex-colleague, warm
> Hi Maya — saw your post about hiring on Payments; congrats on the team's growth. Two quick questions, one easy one bigger: I'm applying to Stripe's Senior Backend role on Payments (link) and wondering if you'd be open to a quick internal referral. Totally fine if timing/role isn't a fit — happy to grab coffee next time I'm in SF either way.

#### Email — former manager
> Subject: Quick ask from your old report 🙂 (and an easy one)
>
> Hi [Name],
>
> Hope you're well — I still think about [specific project you worked on together]. Saw [target company] is hiring for [exact role]; the JD reads like the work we did at [old company], and I wanted to ask if you'd be open to a brief internal referral.
>
> To make it easy: here are the links — JD: [link] · my resume: [link]. If helpful, here's a 2-line blurb you could forward:
>
> *"I've worked with [Name] for [X years] at [Company] on [specific work]. Strong [skills]. Highly recommend for [role]."*
>
> No pressure if the role or timing isn't right — would still love to catch up over coffee next time our paths cross.
>
> Best,
> [You]

#### WeChat — close former colleague
> Hey 老王！好久没聊。注意到你还在 [公司]？他们 [团队] 在招 [岗位]，我特别想试试——方便帮我内推一下吗？JD 链接 [link]，简历 [link]。如果你忙就算啦，下次路过 [城市] 一定请你吃饭 🙂

#### Forward blurb generator (paste-ready for the referrer to forward)

The skill auto-drafts this based on the user's resume + JD. Example output:

> *"[Name] worked with me at [Company] from [years] on [project]. They [1-line credential — e.g. 'owned the migration to gRPC for 12 microservices']. Looking at [Target role] at [Company], this is a near-perfect fit — happy to refer. Reach them at [email]."*

### Step 4: Follow-up Cadence (if no response)

Most referral-asks die in the inbox not because the referrer said no, but because the ask-ers gave up too early. Run this cadence:

| Day | Action | Tone | Length |
|-----|--------|------|--------|
| **Day 0** | Initial send | — | — |
| **Day 7** | Gentle bump | "Bumping this in case it got buried — no rush at all" | ≤300 chars |
| **Day 14** | Different-angle touch | New info: new mutual connection, post they wrote, etc. — *not* "did you see my last msg" | ≤300 chars |
| **Day 21** | Graceful close | "Either way, no worries — appreciate your time. Catch you on the next [community thread/event]" | ≤200 chars |
| **Day 21+** | STOP | Move on | — |

> **Pitfall:** the Day-14 bump should bring *new value* (a relevant post, a mutual intro, a relevant article) — never re-paste the original ask. Re-pasting reads desperate.

### Step 5: Handle Outcomes

The skill produces branched scripts for each outcome:

**Outcome A — Yes, happy to refer:**
- *Your move:* send a thank-you within 24h that includes: (1) the JD link, (2) your resume link, (3) the 2-line forward blurb, (4) any specific team/role preferences. Make their job take <2 minutes.
- *Then:* keep the loop warm. Once a month, send a 1-line update — *"got to onsite, thanks again"* — even if you don't get the offer. These people become future referrers.

**Outcome B — "Can't refer but here's a tip":**
- *Pivot gracefully:* *"That's super helpful, thank you — would it be useful for me to reach out to [their suggestion] directly, or would you rather make the intro?"*
- *Never burn:* even a non-referral is a contact, and they may refer you in 6 months.

**Outcome C — No response after 21 days:**
- *Stop.* Log as "silence" in the ledger. Do not send a 4th message.
- *Optional reach-back:* re-engage 6–12 months later with a non-ask touchpoint (share an article, comment on their post, congratulate a work anniversary).

### Step 6: Track & Iterate (local ledger)

Every ask gets logged to `~/.hermes/data/referrals/ledger.json`:

```json
{
  "asks": [
    {
      "id": "ask-2026-09-15-001",
      "date": "2026-09-15",
      "referrer": "Maya Patel",
      "company": "Stripe",
      "role": "Senior Backend, Payments",
      "channel": "linkedin_dm",
      "tier": "former_colleague",
      "warmth_score": 8,
      "message_sent_chars": 287,
      "follow_up_day_7": true,
      "follow_up_day_14": "different_angle_post_share",
      "follow_up_day_21": "graceful_close",
      "outcome": "yes_referred",
      "response_days": 3,
      "converted_to_interview": true,
      "notes": "Worked together at Acme; her recent hiring post was the hook"
    }
  ],
  "stats": {
    "asks_sent": 14,
    "response_rate": "71%",
    "referral_rate": "43%",
    "interview_conversion_rate": "31%"
  }
}
```

**Surface a weekly digest** on request: *"Show me my referral conversion this month"* — channel-by-channel + tier-by-tier so the user can see whether LinkedIn DMs are converting better than email, or whether weak-tie asks are paying off vs. strong-tie.

### Step 7 (Optional): Cold-Weak-Tie Acquisition Playbook

If the user has **zero 1st-degree contacts at the target**, run this 4-strategy playbook:

1. **Alumni networks** — search LinkedIn filter by `[Your School] + [Target Company]`; reach out with the alumni-connection hook (*"Fellow [School] alum here, working on [thing]"*). Conversion: 15–25%.
2. **Comment-then-DM** — find 3 hiring managers at the target who posted in the last 30 days; leave a substantive comment (not "great post!"); DM them 3 days later referencing the thread. Conversion: 8–15%.
3. **Conference / community mutuals** — check if you both spoke at, attended, or were tagged in the same conference/event/community. Use the shared context as the warm bridge.
4. **Warm 2nd-degree intros** — find someone in *your* network who knows someone at the target. Use the mutual intro path: *"Hey [Mutual] — I noticed you know [Target Person] from [context]. Would you be OK making a 2-line intro? I'll keep it short."* This is the highest-conversion cold path (40–60%) but requires a 2-step ask.

The skill helps draft the **2-step "would you intro me?" ask** as well — it's a different message from the direct referral ask and the user often needs help with it too.

## Example Invocations

### Example 1 — Full warm-intro campaign for one target

> **User:** I want to apply to Stripe for the Senior Backend role on Payments Platform. I have ~600 LinkedIn connections, weak ties mostly. Can you help me get 1–2 referrals?
>
> **Agent:** I'll run Referral Ask Drafter. Quick intake first:
> 1. **JD link?** (paste the URL — I need it for the forward blurb)
> 2. **Resume link?** (LinkedIn / personal site / PDF)
> 3. **What can you offer back?** (informational chat? coffee? relevant intro? a blog post?)
> 4. **Have you talked to anyone at Stripe in the last 6 months?**
>
> *(user pastes JD + LinkedIn URL)*
>
> **Agent:** Got it. Running the network triage against your 1st-degree Stripe connections…
>
> **Top shortlist (3 + 1 stretch):**
> 1. **Maya Patel** — EM @ Payments · ex-Acme teammate · warmth 8/10 · **STRONG**
> 2. **Daniel Kim** — Sr. Eng @ Payments · liked your last 3 posts · warmth 6/10 · **MEDIUM**
> 3. **Priya Subramanian** — Recruiter @ Stripe · never met, but she's been liking your infra posts · warmth 4/10 · **STRETCH**
>
> **Recommended move:** Maya first (highest leverage). Daniel as parallel. Priya as a recruiter-DM (different template).
>
> **Drafting Maya's LinkedIn DM now** *(≤300 chars, ex-colleague-warm template)*:
>
> > Hi Maya — saw your post about hiring on Payments; congrats on the team's growth. Two questions, one easy, one bigger: I'm applying to Stripe's Senior Backend role on Payments ([JD link]) and wondering if you'd be open to a quick internal referral. Totally fine if timing/role isn't a fit — happy to grab coffee next time I'm in SF either way.
>
> **Forward blurb for Maya** *(she can paste this into the referral form)*:
>
> > *"[Name] worked with me at Acme from 2020–2022 on the gRPC migration. Strong systems-design instincts, owned 12 services end-to-end. Looking at the Sr. Backend role on Payments, this is a near-perfect fit. Reach them at [email]."*
>
> **Follow-up cadence** scheduled in your tracker: Day 7 gentle bump, Day 14 different-angle touch, Day 21 graceful close.
>
> Want me to draft Daniel's DM in parallel, or hold until you hear back from Maya?

### Example 2 — Cold-weak-tie acquisition + 2-step intro

> **User:** I want to work at Anthropic but I have zero 1st-degree contacts there. My friend Arjun worked there 2 years ago — he might still know people. How do I get an intro?
>
> **Agent:** Running Step 7 (Cold-Weak-Tie Acquisition). Here's your fastest path:
>
> **Strategy 4 (warm 2nd-degree) — highest conversion, ~50%.**
>
> **Step A — the "would you intro me?" ask to Arjun:**
>
> > Subject: Quick favor (and I owe you one)
> >
> > Hey Arjun,
> >
> > Hope DC is treating you well. Quick favor: I've been deep in the alignment-evaluation space and Anthropic's [specific team] is hiring [role] — looks like exactly what I'd want to do next.
> >
> > I know you moved on in 2024, but I figured you'd still know some folks over there. Would you be comfortable making a 2-line intro to anyone on the [team]? If yes, I'll send you my one-paragraph pitch you can paste directly — keeps it easy.
> >
> > If it's awkward or you've lost touch, totally fine — no pressure at all. I owe you a bourbon either way.
> >
> > Best,
> > [You]
>
> **Step B — once Arjun says yes, your "thank-you + make-it-easy" reply:**
>
> > Perfect, thank you. Here's the one-paragraph pitch — paste directly into your intro:
> >
> > *"Wanted to intro you to [Name] — we worked together at [Company] on [project]. They're now a [current role] with deep experience in [2 things]. Looking at [Anthropic role] on [team], this is a fit. Worth a 20-min chat?"*
> >
> > And here are my links: resume [link] · LinkedIn [link]. Thanks again — buying that bourbon in person next time I'm in DC.

### Example 3 — Chinese-language / WeChat channel

> **User:** 帮我写一条微信，给我前同事老王，他在字节，问他能不能帮我内推后端高级岗。
>
> **Agent:** 已切换到微信模板（≤80 字 hook + 长文切换）。
>
> **微信版：**
>
> > 老王！好久没聊。注意到你还在字节？他们 [团队名] 在招 [后端高级岗]，我特别想试试——方便帮我内推一下吗？JD 链接 [link]，简历 [link]。要是忙就算啦，下次路过 [城市] 一定请你吃饭 🙂
>
> **如果是关系更近一点（多年搭档）：**
>
> > 王哥！两没见。最近看你还在字节？[团队] 在招 [岗位]，感觉是给我量身定做的，能帮我推一下不？JD 我发你，简历也在 [link]。方便的话回个 1 我把材料包整理好给你，2 分钟搞定。
>
> **跟进节奏**（已在你的 ledger 里登记）：
> - Day 7 轻推："在吗？上面的事再问一嘴，不急 🙂"
> - Day 14 转角度：你最近发的 [某条朋友圈 / 某篇文章] 转给他，附一句"看完想起你的工作，先不打扰了，内推的事方便再说"
> - Day 21 礼貌收："算了不催了，下次见面聊！"

## Common Pitfalls

| Pitfall | Why It Fails | Fix |
|---------|-------------|-----|
| **Long first LinkedIn message** (>500 chars) | LinkedIn truncates at ~300 chars on mobile; long intros read like a cover letter | Keep first DM ≤300 chars; expand only after they reply |
| **"I'm reaching out because…" opening** | Sounds like a sales pitch, triggers "scam filter" | Open with a *specific* shared context or their recent activity |
| **Asking without making it easy** | Referrers say no because they don't want to do work | Always include JD link + resume link + 2-line forward blurb |
| **Apologizing for asking** ("sorry to bother") | Sub-communicates you think the ask is illegitimate | Drop the apology; the graceful-out line replaces it |
| **Following up with the same message** | Reads as "did you see my last msg?" — pushy | Each follow-up must bring *new value* (their post, an article, a mutual connection) |
| **Sending the same template to 20 people** | Recipients compare notes; if 3 of them are mutuals, you'll get caught | Personalize every message with a specific shared context or observation |
| **Asking someone who's been at the company <6 months** | Most companies require 6+ months tenure to refer | Filter the shortlist by tenure |
| **Asking a peer instead of a senior** | A peer intro has weak pull; they can't sell your seniority | Senior / former-manager intros convert 2–3× better |
| **Burning the relationship with no thank-you** | You got the referral, you vanished, they tell their team you were rude | Within 24h of a yes: thank-you + JD/resume/blurb + update them on the process |
| **Continuing to ping after 21 days of silence** | Damages the relationship permanently | Stop. Re-engage 6+ months later with non-ask content |
| **Asking for a referral to a role that doesn't fit** | Referrer says no, then you look unserious | Re-check the JD yourself; if <60% match, don't ask this person |
| **Asking only recruiters** | Recruiters don't refer — they screen; using them as referrers is misframed | Reserve recruiters for a separate "introscreen" ask (different template) |

## Verification Checklist

Before sending any referral-ask:

- [ ] Target company + role confirmed and match is >60%
- [ ] JD link and resume link ready (no attachments)
- [ ] Referrer confirmed at target company with >6 months tenure
- [ ] Relationship-tier classified (cold-weak / acquaintance / ex-colleague / former-manager)
- [ ] Channel chosen and message ≤length limit
- [ ] First sentence references *specific* shared context or their recent activity
- [ ] Forward blurb pre-drafted so the referrer can paste it
- [ ] Graceful-out line included ("no worries either way")
- [ ] No apology, no "hope this finds you well," no emojis in professional channels
- [ ] Spelled the referrer's name correctly (do NOT rely on auto-complete — verify in their recent post or profile)
- [ ] Sent during their business hours (Tue–Thu 9–11am local time converts ~30% better than Friday afternoon)
- [ ] Logged in `~/.hermes/data/referrals/ledger.json`
- [ ] Follow-up cadence scheduled (Day 7 / Day 14 / Day 21)

After sending:

- [ ] Within 24h of any yes: thank-you + JD + resume + blurb sent
- [ ] Outcome logged in ledger (yes / no-but-tip / silent / declined)
- [ ] If converted to interview, update the user once during process + once at outcome (regardless of result — keeps the loop warm)

## Data Sources & Accuracy

This skill is **craft-based** — the templates are drawn from publicly known networking best practices (LinkedIn's own recruiter guides, hiring-manager surveys, "weak ties" research from Granovetter 1973 + subsequent replication studies, alumni-network conversion studies from career-services offices), not from any proprietary data source. All message templates are the skill author's own composition, not lifted from any third-party service.

**Privacy guarantees:**
- **No LinkedIn automation / scraping.** This skill does *not* script LinkedIn actions, harvest emails, or impersonate users. Every send is the user manually clicking send.
- **No contact uploads.** The user's CRM data stays local; if used, only file paths on the user's own machine are referenced.
- **No third-party tracking.** No pixels, no UTM tracking on the DMs, no referral-attribution back to any service.

**Accuracy caveat:** conversion rates and tier weights in Step 2 are based on aggregate industry-survey ranges and the skill author's synthesis of multiple career-coaching sources, not a controlled study. Use them as a heuristic, not a guarantee. The skill encourages the user to track *their own* rates in the ledger — those local numbers will beat any published estimate after 10+ asks.

**Localization:** US English templates default; Chinese (微信 / 邮件 / 领英) templates are culture-adapted (different openings, different graceful-out phrasing, no "hope this finds you well" which reads oddly in 中文). For German / French / Japanese / Hindi / Spanish channels, the skill will adapt the structure but ask the user to confirm 1–2 native-phrasing details — this is craft, not translation.

---

*P.S. If this skill got you an interview: drop a one-time thank-you to whoever referred you, even if you don't get the offer. They'll refer someone else for you in 2 years.*