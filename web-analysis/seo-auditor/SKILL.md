---
name: seo-auditor
description: "Analyze any website's SEO health — meta tags, headings, structured data, page speed indicators, robots.txt, sitemap, Open Graph, and more."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [web-analysis, seo, search-engine-optimization, website-audit, digital-marketing]
    related_skills: [tech-stack-detector, competitive-research, report-formatter]
---

# SEO Auditor / SEO 网站审计

> Analyze any public URL and produce a structured SEO health report covering on-page SEO, technical SEO, content structure, and social sharing metadata.

---

## Overview

This skill performs a comprehensive on-page and technical SEO audit of any public URL. It uses HTTP inspection, HTML parsing, and content analysis to evaluate search-engine-friendliness across multiple dimensions — without requiring any third-party API keys or subscription services.

**What it checks:**

| SEO Dimension | What's Inspected |
|---------------|------------------|
| **Meta Tags** | Title tag, meta description, meta robots, canonical URL, language/hreflang |
| **Heading Structure** | H1–H6 hierarchy, H1 uniqueness, heading gaps |
| **Structured Data** | JSON-LD / Microdata / RDFa schema types detected |
| **Social Sharing** | Open Graph (og:*) and Twitter Card tags |
| **Technical SEO** | robots.txt accessibility, sitemap.xml existence, status code, redirect chain |
| **Content SEO** | Word count, keyword density, image alt attributes, internal link count |
| **Mobile & Performance** | Viewport meta tag, content width hints, render-blocking resource indicators |
| **Security** | HTTPS enforcement, HSTS header, mixed content warnings |
| **URL Structure** | URL length, query params, path depth, trailing slash consistency |

---

## When to Use

- **"Audit the SEO of my website"** — before or after a redesign, content update, or migration
- **"Check a competitor's on-page SEO"** — competitive intelligence to see what they're optimizing for
- **"Is this page SEO-friendly?"** — quick sanity check before publishing a landing page or blog post
- **"Can you generate an SEO report for example.com?"** — shareable report for stakeholders or clients
- **"What's missing from my meta tags?"** — onboarding a new site or diagnosing low traffic

---

## Core Workflow

### Step 1: Fetch & Inspect the URL

Use `curl` to fetch the page and headers:

```bash
# Fetch full page + response headers
curl -sSL -D - "https://example.com" -o /tmp/seo_page.html 2>&1
```

```bash
# Extract response headers separately
curl -sI "https://example.com"
```

Check for:
- **Status code**: 200 is ideal. 301/302 = check redirect chain. 404/500 = critical issue.
- **Redirect chain**: Track `-L` follow count. Multiple redirects hurt SEO.
- **HTTPS**: Ensure the final URL uses HTTPS.
- **HSTS header** (`Strict-Transport-Security`): present = good.

### Step 2: Extract & Analyze HTML

Parse the saved HTML file to extract key SEO elements.

**2a. Meta tags:**
```bash
# Title tag
grep -oP '<title[^>]*>.*?</title>' /tmp/seo_page.html

# Meta description
grep -oP '<meta[^>]+name=["'"'"']description["'"'"'][^>]*>' /tmp/seo_page.html

# Meta robots
grep -oP '<meta[^>]+name=["'"'"']robots["'"'"'][^>]*>' /tmp/seo_page.html

# Canonical URL
grep -oP '<link[^>]+rel=["'"'"']canonical["'"'"'][^>]*>' /tmp/seo_page.html

# Hreflang tags
grep -oP '<link[^>]+rel=["'"'"']alternate["'"'"'][^>]*hreflang[^>]*>' /tmp/seo_page.html
```

**2b. Heading structure:**
```bash
# Extract all headings with their level
grep -oP '<h[1-6][^>]*>.*?</h[1-6]>' /tmp/seo_page.html

# Count headings by level
for i in 1 2 3 4 5 6; do
  count=$(grep -cP "<h$i[ >]" /tmp/seo_page.html)
  echo "H$i: $count"
done
```

Check: Exactly one H1? H2–H6 hierarchy respected? No heading level skips (H1→H3 without H2)?

**2c. Structured data (JSON-LD / Schema):**
```bash
# Extract JSON-LD blocks
grep -oP '<script[^>]+type=["'"'"']application/ld\+json["'"'"'][^>]*>.*?</script>' /tmp/seo_page.html | sed 's/<[^>]*>//g'

# Extract Microdata item types
grep -oP 'itemtype=["'"'"']https?://schema\.org/[^"'"'"']+' /tmp/seo_page.html | sort -u
```

**2d. Open Graph & Twitter Cards:**
```bash
# Open Graph tags
grep -oP '<meta[^>]+property=["'"'"']og:[^"'"'"']*["'"'"'][^>]*>' /tmp/seo_page.html

# Twitter Card tags
grep -oP '<meta[^>]+name=["'"'"']twitter:[^"'"'"']*["'"'"'][^>]*>' /tmp/seo_page.html
```

**2e. Image alt attributes:**
```bash
# Images WITH alt text
grep -oP '<img[^>]+alt=["'"'"'][^"'"]*["'"'"']' /tmp/seo_page.html | wc -l

# Images WITHOUT alt text (decorative images without alt="" are flagged)
grep -oP '<img[^>]*>' /tmp/seo_page.html | grep -vP 'alt=["'"'"']' | wc -l

# Total images
grep -cP '<img[ >]' /tmp/seo_page.html
```

**2f. Content analysis:**
```bash
# Extract visible text content (rough word count)
sed 's/<[^>]*>//g' /tmp/seo_page.html | tr -s ' \n' ' ' | wc -w

# Internal vs external links
grep -oP 'href=["'"'"']https?://[^"'"'"']*["'"'"']' /tmp/seo_page.html | sort -u
```

### Step 3: Check Technical SEO Infrastructure

**3a. robots.txt:**
```bash
curl -sI "https://example.com/robots.txt" | head -5
curl -s "https://example.com/robots.txt"
```

Flag if: status is 404 (no robots.txt), or if `Disallow: /` exists (blocks all crawlers).

**3b. Sitemap:**
```bash
curl -sI "https://example.com/sitemap.xml"
curl -sI "https://example.com/sitemap_index.xml"
```

Also check if sitemap is referenced in robots.txt.

**3c. Viewport / Mobile indicators:**
```bash
grep -oP '<meta[^>]+name=["'"'"']viewport["'"'"'][^>]*>' /tmp/seo_page.html
```

**3d. Performance indicators:**
```bash
# Number of external CSS/JS requests (render blocking indicator)
grep -cP '<link[^>]+rel=["'"'"']stylesheet["'"'"']' /tmp/seo_page.html
grep -cP '<script[^>]+src=["'"'"']' /tmp/seo_page.html
```

Flag if: more than 3 CSS files or more than 10 JS files (potential performance bottleneck).

**3e. Check for mixed content (HTTP resources on HTTPS page):**
```bash
grep -oP 'src=["'"'"']http://[^"'"'"']*["'"'"']' /tmp/seo_page.html
grep -oP 'href=["'"'"']http://[^"'"'"']*["'"'"']' /tmp/seo_page.html
```

### Step 4: Generate the SEO Report

Compile findings into a structured report with:

| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90–100 | 🟢 Excellent | Well optimized. Minor improvements. |
| 70–89 | 🟡 Good | Mostly optimized. Some issues to fix. |
| 50–69 | 🟠 Needs Work | Significant gaps found. Prioritize fixes. |
| 0–49 | 🔴 Critical | Major SEO issues present. |

**Scoring guide (approximate):**
- Meta tags (title + description present + well-written): **20 pts**
- Heading structure (1 H1, logical hierarchy): **15 pts**
- Structured data present: **15 pts**
- Social tags (OG + Twitter): **10 pts**
- Robots.txt + Sitemap present: **10 pts**
- HTTPS + HSTS: **10 pts**
- Viewport meta tag (mobile-friendly): **10 pts**
- Alt text on images (≥80% have alt): **5 pts**
- No mixed content: **5 pts**

Present the report in markdown format with clear sections and actionable recommendations.

---

## Example Invocations

### Example 1: SEO health check for a personal blog

**User:** "Audit my blog at https://example-blog.com for SEO"

**Agent action:**
1. Fetches the page with curl, captures headers and HTML
2. Checks status code (200 ✓), HTTPS (✓), HSTS header (missing)
3. Extracts title tag ("My Awesome Blog | Home"), meta description (missing!), meta robots (index,follow ✓)
4. Finds H1: 2 H1 tags (flag: multiple H1s)
5. Finds JSON-LD schema (BlogPosting ✓)
6. Checks robots.txt (200 ✓, no sitemap reference), sitemap.xml (200 ✓)
7. Detects viewport meta tag (present ✓), 4 CSS files, 12 JS files
8. Generates report:

```markdown
## SEO Audit: https://example-blog.com

**Score: 72/100 🟡 Good**

### Issues Found
- ⚠️ **Meta description missing** — critical for search snippets
- ⚠️ **2 H1 tags found** — should be exactly one per page
- ⚠️ **No HSTS header** — minor HTTPS security signal
- ⚠️ **12 JavaScript files** — may slow page load

### Recommendations
1. Add `<meta name="description">` with a compelling 150-160 char summary
2. Consolidate H1 tags into a single descriptive heading
3. Enforce HSTS via web server config
4. Bundle and defer JS where possible
```

### Example 2: Competitor SEO intelligence

**User:** "What SEO meta tags does stripe.com use?"

**Agent action:**
1. Fetches https://stripe.com with curl
2. Extracts: Title (81 chars ✓), Description (155 chars ✓), Canonical URL (✓)
3. Finds Open Graph tags (og:title, og:description, og:image, og:url ✓)
4. Finds Twitter Card tags (twitter:card=summary_large_image ✓)
5. Checks JSON-LD (Organization schema with logo, sameAs URLs ✓)
6. Verifies HTTPS (✓), HSTS (✓), robots.txt (✓ with sitemap reference)
7. Reports findings as structured markdown

### Example 3: Pre-launch SEO checklist

**User:** "Check if my landing page at https://mynewproduct.io/launch is SEO-ready before we go live"

**Agent action:**
1. Full crawl: status code, redirects, all meta tags
2. Checks for: robots meta tag (noindex?), canonical URL set correctly
3. Content analysis: word count (320 words — below 600 recommended)
4. Image alt check: 3 images, 0 with alt text
5. Structured data: Product schema missing
6. Generates pre-launch report with must-fix (alt text, more content) and nice-to-have (schema, social tags) buckets

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **JavaScript-rendered content** | `curl` only sees server-rendered HTML. Note in report: "Content may differ from browser-rendered DOM. For SPA sites (React/Vue/Angular), consider checking server-side rendering or prerendering setup." |
| **Large pages timeout** | Increase curl timeout: `curl -sSL --max-time 30 "https://..."` |
| **Website blocks curl** | Add a common User-Agent header: `curl -sSL -A "Mozilla/5.0 ..." "https://..."` |
| **Sitemap at non-standard path** | Check robots.txt for `Sitemap:` directive — it may point to `/sitemap.php` or `/sitemap-index.xml` |
| **Redirect chains obscure results** | Use `curl -sSL -D -` to capture every hop, then analyze the final page content |
| **Dynamic page content varies per visit** | Run the audit 2–3 times over different hours to get a representative sample |
| **Can't determine keyword focus** | Use web_search to find the page's ranking keywords for context |

---

## Verification Checklist

- [ ] Page returns HTTP 200 (no redirects or errors)
- [ ] HTTPS enforced (HTTP → 301 → HTTPS)
- [ ] Title tag present, unique, and 50–60 characters
- [ ] Meta description present and 150–160 characters
- [ ] Meta robots allows indexing (no `noindex`)
- [ ] Canonical URL self-referencing or correctly set
- [ ] Exactly one H1 tag present
- [ ] Heading hierarchy logical (no skipped levels)
- [ ] Structured data (JSON-LD or Microdata) found and valid
- [ ] Open Graph tags present (og:title, og:description, og:image)
- [ ] Twitter Card tags present
- [ ] robots.txt accessible (HTTP 200)
- [ ] sitemap.xml accessible
- [ ] Viewport meta tag present
- [ ] Alt text present on ≥80% of images
- [ ] No mixed content (HTTP assets on HTTPS page)
- [ ] HSTS header present (recommended)
- [ ] Report generated with score, issues, and recommendations

---

## Data Sources & Accuracy

- **Page content**: Fetched directly via HTTP GET at audit time. Represents server-rendered HTML only. Single-page applications (SPAs) may render additional content client-side that is not visible to curl/static analysis.
- **Status & headers**: Real-time HTTP response data. Network conditions and server load may affect latency observations.
- **Schema detection**: Regex-based extraction identifies known structured data patterns. Nested or malformed JSON-LD may not be fully parsed — use a validator like Google's Rich Results Test for authoritative validation.
- **Redirect chains**: Captured using curl's `-L` flag with `-D -` for header dump. Intermediate response bodies are not inspected.
- **No external API dependency**: This skill operates entirely via curl and standard Unix tools (grep, sed, wc). No third-party SEO APIs or subscriptions required.
- **Limitations**: Does not measure actual load times, Core Web Vitals (LCP, CLS, INP), backlink profiles, keyword rankings, or crawl budget allocation. These require browser-based or specialized third-party tools.
