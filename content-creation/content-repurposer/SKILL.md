---
name: content-repurposer
description: "Use when transforming existing content (blog posts, articles, videos, transcripts, podcasts) into multiple formats for different platforms — Twitter threads, LinkedIn posts, 小红书文案, summaries, and more."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [content-creation, social-media, repurposing, marketing, twitter, linkedin, xiaohongshu, multilingual]
    related_skills: [newsletter-digest, blog-post-writer, writing-plans]
---

# Content Repurposer

> Transform a single piece of content into multiple formats optimized for different platforms. One article, blog post, video URL, or transcript → Twitter thread, LinkedIn post, 小红书文案, newsletter blurb, key takeaways, and more.

---

## Overview

This skill takes one source of content (a blog post URL, a YouTube video, a podcast transcript, or raw text) and repurposes it into multiple platform-optimized formats. Instead of writing separate content for every channel, create once and distribute everywhere.

Each output format is tailored to the platform's conventions: character limits, tone, formatting, hashtag usage, and audience expectations.

**Supported input types:**
| Input | Example |
|-------|---------|
| **Blog post URL** | `https://example.com/blog/post` |
| **YouTube video** | `https://youtube.com/watch?v=...` |
| **Podcast episode** | Spotify/Apple podcast link or transcript |
| **Raw text** | Direct text paste |
| **PDF / document** | File path |

**Supported output formats:**
| Platform | Format | Best For |
|----------|--------|----------|
| **Twitter / X** | Thread (5-15 tweets) | Quick engagement, viral reach |
| **LinkedIn** | Long-form post (300-1500 chars) | Professional audience, B2B |
| **小红书 (Xiaohongshu)** | 种草笔记 (500-1000 chars + emoji + hashtags) | Chinese social commerce |
| **Newsletter blurb** | 2-3 paragraph summary | Email subscribers |
| **Key Takeaways** | Bulleted list (3-7 points) | Skimmers, quick reference |
| **Executive Summary** | 1-paragraph TL;DR | Busy decision-makers |
| **Quote cards** | 3-5 quotable snippets | Visual social posts |

---

## When to Use

- User asks: *"Turn this blog post into a Twitter thread and LinkedIn post"*
- User asks: *"帮我把我这篇英文文章改成小红书文案"*
- User asks: *"Repurpose this YouTube video into a newsletter blurb"*
- User asks: *"Give me key takeaways from this article"*
- User asks: *"Create social media posts for this podcast episode"*

---

## Core Workflow

### Step 1: Ingest Source Content

Depending on the input type, extract the content:

#### For URLs (blog posts, articles):
```bash
curl -sL {url} 2>&1
```
Then extract the main body text — strip navigation, ads, and boilerplate. Focus on:
- Title and subtitle
- Introduction / thesis
- Key arguments or sections (H2/H3 headings)
- Conclusion / call to action

#### For YouTube videos:
If the video URL is provided, try to fetch the transcript (via YouTube API or subtitle extraction). If transcript isn't available, watch or read the video description and visible content.

#### For raw text / paste:
Use the provided text directly. Note the approximate word count.

#### For PDFs / documents:
Use file reading tools to extract text content.

### Step 2: Understand the Core Message

Before repurposing, distill the content into its essence:

```
Main thesis: {one sentence}
Target audience: {who is this for?}
Key points (3-5): {bullet list}
Tone: {professional / casual / humorous / educational}
Call to action: {what should the reader do?}
```

### Step 3: Generate Platform-Specific Outputs

Generate each requested format. Follow the platform conventions below:

#### 🐦 Twitter / X Thread

```
1/ {Hook — provocative question or bold statement}
🧵

2/ {Context — why this matters now}

3/ {Insight 1 — the first key point}
   {Supporting detail or example}

4/ {Insight 2 — the second key point}

5/ {Insight 3 — the third key point}

...

{N-1}/{N} {Summary — tie it all together}
   {Key takeaway in one line}

{N}/{N} {Call to action}
   {Question to drive engagement}

#️⃣ {1-3 relevant hashtags}
```

**Rules:**
- Each tweet: ≤280 chars (hard limit)
- Use `🧵` to signal it's a thread
- Number all tweets: `1/8`, `2/8`, etc.
- Hook in tweet 1 is critical
- Use line breaks within tweets for readability
- 3-5 emojis max per thread
- Hashtags only in the last tweet
- Always end with a question or CTA

#### 💼 LinkedIn Post

```
{Headline or bold opening statement}

{2-3 paragraph body}

Paragraph 1: Hook + context (why this matters)
Paragraph 2: The insight or lesson
Paragraph 3: Personal take / application

💡 Key takeaway: {one-liner}

🤔 Question for you: {engagement-driving question}

#️⃣{Hashtag1} #{Hashtag2} #{Hashtag3}
```

**Rules:**
- 300-1500 chars (optimal: 600-1200)
- Professional but conversational tone
- Line breaks between paragraphs
- 1-2 emojis max (subtle, not excessive)
- 3-5 relevant hashtags
- End with a question to drive comments
- Use "I" and personal experience when possible

#### 🎀 小红书 (Xiaohongshu) — 种草笔记

```
{Emoji-rich title — 15-20 chars optimal}

📌 {Subtitle or key benefit}

正文结构：
1. 开头 (Hook — 引起共鸣):
   "姐妹们！我终于找到了..." / "做了3个月的功课..."

2. 核心内容 (Main body — 价值输出):
   - 要点1: {描述}
   - 要点2: {描述}
   - 要点3: {描述}

3. 总结 (Closing — 引导互动):
   个人感受 + 建议

#️⃣#{话题标签1} #{话题标签2} #{话题标签3} #{话题标签4} #{话题标签5}
```

**Rules:**
- 500-1000 chars optimal
- Emoji-rich (3-8 emojis per post)
- Conversational, friendly tone
- Use line breaks for readability
- 3-5 relevant hashtags
- Avoid overly promotional language
- Include personal experience / POV
- Save the best tip for the end (惊喜感)

#### 📧 Newsletter Blurb

```
**{Catchy headline}**

{2-3 paragraphs}

Intro: Hook + why this matters
Body: Key insight or finding
Closing: What to do about it / why it's relevant to subscribers

[Read full article →]({url})
```

**Rules:**
- 150-300 words
- Concise — subscribers skim
- Link back to full source
- Make it self-contained (works without clicking through)

#### 📋 Key Takeaways

```
**{Title}** — Key Takeaways

✅ {Takeaway 1} — {one-sentence explanation}
✅ {Takeaway 2} — {one-sentence explanation}
✅ {Takeaway 3} — {one-sentence explanation}
✅ {Takeaway 4} — {one-sentence explanation}
✅ {Takeaway 5} — {one-sentence explanation}

📖 [Full article]({url})
```

**Rules:**
- 3-7 bullet points
- One sentence each
- Actionable — "what to do" not "what it says"
- Include source link

### Step 4: Save Output

Save all generated formats to a file:

```
~/content/{source-title}/YYYY-MM-DD-repurposed.md
```

Structure the output with clear section headers for each format.

---

## Example Invocations

### Example 1: Blog → Twitter + LinkedIn + Newsletter
```
User: Repurpose this article into a Twitter thread, LinkedIn post, and newsletter blurb:
https://example.com/how-to-build-a-startup
Hermes should:
  1. Fetch and read the article
  2. Extract core thesis and key points
  3. Generate Twitter thread (8 tweets)
  4. Generate LinkedIn post (800 chars)
  5. Generate newsletter blurb (200 words)
  6. Save all formats to file
  7. Present all three outputs
```

### Example 2: English → Chinese social media
```
User: 把这篇英文博文改成小红书文案和LinkedIn中文帖子
https://example.com/ai-trends-2026
Hermes should:
  1. Read the English article
  2. Distill core message
  3. Generate 小红书种草笔记 (800字, emoji, hashtags)
  4. Generate LinkedIn 中文帖子
  5. Save and present
```

### Example 3: YouTube video → Key takeaways
```
User: Give me key takeaways from this talk and a Twitter thread:
https://youtube.com/watch?v=abc123
Hermes should:
  1. Fetch video transcript or watch
  2. Extract 5 key takeaways
  3. Generate a Twitter thread summarizing
  4. Save and present
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Twitter thread tweets exceed 280 chars.** | Count chars carefully. Split long points into 2 tweets. |
| 2 | **小红书 tone too promotional.** | Use genuine, personal tone — "种草" not "广告". Add personal experience. |
| 3 | **LinkedIn post too short / too long.** | Aim for 600-1200 chars. If content is thin, expand with personal take. |
| 4 | **Repurposing loses the original's nuance.** | Always preserve the core argument and key evidence. Don't oversimplify complex topics. |
| 5 | **Same content, same words, different format.** | Rewrite for each platform — don't just add emojis. Adapt tone, structure, and emphasis. |
| 6 | **Missing call to action.** | Every format needs a CTA: question (Twitter/LinkedIn), follow/save (小红书), subscribe (newsletter). |
| 7 | **Chinese content has wrong tone for 小红书.** | Study the platform: use 姐妹们, 亲测, 吐血整理, 干货 style. Not formal/technical. |

---

## Content Tone Reference

| Platform | Tone | Sentence Length | Emoji | Hashtags | Call to Action |
|----------|------|----------------|-------|----------|----------------|
| Twitter / X | Punchy, opinionated | Short (20-40 chars) | 3-5 total | 1-3 (last tweet) | Question or poll |
| LinkedIn | Professional, story-driven | Medium (40-80 chars) | 1-3 subtle | 3-5 | "What's your take?" |
| 小红书 | Friendly, personal, "姐妹" | Medium (30-60 chars) | 5-10 | 3-5 | "收藏" / "关注" |
| Newsletter | Conversational, value-first | Medium (40-100 chars) | 1-2 | 0 | "Reply with thoughts" |
| Key Takeaways | Direct, actionable | Short (15-30 chars) | ✅ markers | 0 | "Read full article" |

---

## Verification Checklist

- [ ] Source content ingested and understood
- [ ] Core thesis distilled (one sentence)
- [ ] Each requested format follows platform conventions
- [ ] Twitter thread: ≤280 chars per tweet, numbered, hook + CTA
- [ ] LinkedIn post: 600-1200 chars, conversational, question at end
- [ ] 小红书: emoji-rich, personal tone, hashtags, 种草 style
- [ ] All outputs include source attribution
- [ ] Saved to `~/content/{title}/`
- [ ] Language matches user's request
