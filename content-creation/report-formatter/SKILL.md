---
name: report-formatter
description: "Use when sharing analysis reports with friends or social media — converts research/business reports into WeChat posts, Instagram stories, Twitter threads, simple HTML pages, or text summaries."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [sharing, formatting, social-media, wechat, instagram, twitter, html]
    related_skills: [content-repurposer, twitter-thread-writer, presentation-helper]
---

# Report Formatter

> Turn any analysis report into a shareable format for friends. Supports WeChat posts, Instagram stories, Twitter threads, simple HTML pages, and clean text summaries.

---

## When to Use

- *"把这个选址报告转成微信可以发的格式"*
- *"Turn this business plan into a shareable webpage for my partner"*
- *"Make an Instagram story from this competitor analysis"*
- *"帮我总结这个报告，发给我朋友看看"*
- *"Create a simple HTML page from this site analysis"*

---

## Core Workflow

### Step 1: Read the Report

Read the source report file. Identify:
- **Title** — what's this about?
- **Key findings** — the 3-5 most important takeaways
- **Data points** — numbers, rankings, scores
- **Recommendations** — what should the reader do?
- **Tone** — formal research / business pitch / casual analysis

### Step 2: Choose Format

Ask the user which format(s) they want:

| Format | Best For | Length |
|--------|----------|--------|
| **📱 WeChat (微信朋友圈)** | Chinese social sharing | 200-500字 + emoji |
| **📸 Instagram Story** | Visual storytelling | 5-10 slides of text |
| **🐦 Twitter Thread** | English social sharing | 5-10 tweets |
| **🌐 Simple HTML** | Shareable webpage (link) | Full report |
| **💬 Text Summary** | iMessage / WhatsApp | 100-300 words |
| **📄 Clean Markdown** | Tech-savvy friends | Full report |

### Step 3: Generate Output

#### 📱 WeChat 朋友圈格式

Keep it casual, personal, and emoji-rich. Chinese only.

```
{Emoji-rich opening — 1-2 sentences hook}

📊 关键发现：
• {Finding 1}
• {Finding 2}
• {Finding 3}

💡 我的想法：
{2-3 sentences personal take}

📍 完整报告已保存，想看的私信我～
```

**Rules:**
- 200-500 字
- 3-5 emoji
- 口语化，像跟朋友聊天
- 不要用专业术语
- 结尾引导互动（私信、评论）

#### 📸 Instagram Story Format

Designed as text overlay for story slides.

```
Slide 1: {Title} + eye-catching emoji
Slide 2: 📊 The Big Finding — {one key number}
Slide 3: 🎯 Key Insight — {one sentence}
Slide 4: 💡 Bottom Line — {recommendation}
Slide 5: 👆 DM me for the full report!
```

**Rules:**
- Each slide: 1 line of text max
- Big numbers stand alone
- Use Instagram-friendly emojis
- End with a CTA to DM

#### 🐦 Twitter Thread

Extract 5-8 key tweets from the report.

```
1/8 {Hook — surprising finding or bold claim} 🧵
2/8 {Context — what we analyzed}
3/8 {Finding 1 — with number}
4/8 {Finding 2 — with number}
5/8 {Insight — what it means}
6/8 {Recommendation — what to do}
7/8 {Bottom line in one sentence}
8/8 Full report → {link or "DM me"} #topic
```

**Rules:**
- ≤280 chars per tweet (enforce)
- Use 🧵 in tweet 1
- Number all tweets: 1/8, 2/8
- End with CTA

#### 🌐 Simple HTML Page

Generate a standalone HTML file that looks clean on mobile.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{Title}</title>
  <style>
    body { font-family: -apple-system, sans-serif; max-width: 640px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }
    h1 { font-size: 24px; }
    h2 { font-size: 18px; margin-top: 24px; }
    .highlight { background: #fff3cd; padding: 12px; border-radius: 8px; }
    table { width: 100%; border-collapse: collapse; }
    td, th { padding: 8px; border-bottom: 1px solid #eee; text-align: left; }
    .emoji { font-size: 20px; }
    @media (prefers-color-scheme: dark) {
      body { background: #1a1a2e; color: #e0e0e0; }
      td, th { border-bottom-color: #333; }
      .highlight { background: #2d2d44; }
    }
  </style>
</head>
<body>
  {Report content formatted as clean HTML}
</body>
</html>
```

**Rules:**
- Self-contained (no external CSS/JS)
- Dark mode support
- Mobile-responsive
- Emojis render natively

#### 💬 Text Summary (iMessage / WhatsApp)

Short, punchy, no formatting.

```
📊 {Title}

The key finding: {one sentence}

{3 bullet points of key data}

Bottom line: {recommendation}

Full report saved — want the details?
```

**Rules:**
- 100-300 words
- No markdown formatting (plain text)
- Emoji-supported
- Ends with a question to keep conversation going

### Step 4: Save Output

Save the formatted output:

```
~/dev/reports/shared/{report-name}/
├── wechat-post.md
├── twitter-thread.md
├── instagram-story.txt
├── shareable-page.html
└── text-summary.txt
```

Offer to open the HTML file in browser for the user to preview.

---

## Example Invocations

### Example 1: WeChat post from site analysis
```
User: 帮我把这个选址报告转成微信朋友圈格式
       ~/dev/reports/site-analysis/2026-06-17-ramen-dumpling-complete-report.md
Hermes should:
  1. Read the report → extract key findings
  2. Generate WeChat post (300字, emoji, casual tone)
  3. Save to ~/dev/reports/shared/ramen-site-analysis/wechat-post.md
  4. Present the post
```

### Example 2: Twitter thread from business plan
```
User: Turn my business plan into a Twitter thread
       ~/dev/reports/business-plans/2026-06-17-gyoza-noodles-business-plan.md
Hermes should:
  1. Read the plan → extract key points
  2. Generate 8-tweet thread
  3. Save to ~/dev/reports/shared/gyoza-plan/twitter-thread.md
  4. Verify each tweet ≤ 280 chars
```

### Example 3: HTML page + all formats
```
User: Generate all shareable formats for this competitor analysis
Hermes should:
  1. Read the report
  2. Generate WeChat + Twitter + Instagram + HTML + Text
  3. Save all to ~/dev/reports/shared/{name}/
  4. Present all outputs
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **WeChat post too formal/long.** | Keep it conversational. 200-500 chars. Think "telling a friend". |
| 2 | **Twitter tweets exceed 280 chars.** | Count chars. Split long points into 2 tweets. |
| 3 | **HTML page has broken emoji.** | Use native emoji (😊), not icon fonts or images. |
| 4 | **Instagram story text too long.** | Max 1 line per slide. Use big numbers. |
| 5 | **Text summary still has markdown.** | Strip all `**`, `##`, `- ` formatting for plain text. |

---

## Verification Checklist

- [ ] Source report read and understood
- [ ] Key findings extracted (3-5)
- [ ] WeChat: ≤500 chars, emoji, casual tone
- [ ] Twitter: ≤280/tweet, numbered, 🧵, CTA
- [ ] Instagram: 1 line/slide, big number on slide 2
- [ ] HTML: self-contained, dark mode, mobile-responsive
- [ ] Text summary: plain text, 100-300 words
- [ ] All outputs saved to `~/dev/reports/shared/{name}/`
- [ ] HTML file opened in browser for preview (if requested)
