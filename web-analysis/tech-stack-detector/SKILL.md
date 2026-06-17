---
name: tech-stack-detector
description: "Use when analyzing a website's technology stack — detect frameworks, CDNs, analytics, hosting, and JS libraries from any URL."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [web-analysis, technology, reconnaissance, tech-stack, competitive-intelligence]
    related_skills: [local-competitive-analysis, competitive-research, writing-plans]
---

# Tech Stack Detector

> Analyze a website's technology stack — detect frameworks, CDNs, analytics, hosting providers, JS libraries, and more from any URL.

---

## Overview

This skill inspects a given URL and identifies the technologies powering it. It uses multiple detection techniques: HTTP headers, HTML inspection, JavaScript globals, CSS analysis, CDN patterns, and DNS lookups. The result is a structured report showing what a website is built with.

Perfect for competitive intelligence, tech recruitment ("who uses React in this city?"), or just satisfying your curiosity about how a site is built.

**What it can detect:**
| Category | Examples |
|----------|----------|
| **Web frameworks** | React, Vue, Angular, Next.js, Nuxt, Svelte, Astro, Django, Rails, Laravel |
| **CSS frameworks** | Tailwind, Bootstrap, Material UI, Chakra, Bulma |
| **CDN / Hosting** | Cloudflare, CloudFront, Fastly, Vercel, Netlify, AWS, GCP |
| **Analytics** | Google Analytics, Plausible, Umami, Mixpanel, Heap, Hotjar |
| **JavaScript libraries** | jQuery, Alpine.js, htmx, Three.js, D3, Lodash |
| **CMS** | WordPress, Shopify, Squarespace, Wix, Sanity, Contentful |
| **Servers / Runtimes** | Nginx, Apache, Caddy, Node.js, Python, Ruby, Go |
| **SSL / Certificates** | Let's Encrypt, Cloudflare, DigiCert, Sectigo |

---

## When to Use

- User asks: *"What tech stack does stripe.com use?"*
- User asks: *"Analyze this website: https://example.com"*
- User asks: *"Check what framework my competitor's site is built with"*
- User asks: *"What hosting does this site use?"*
- User asks: *"Is this site using React or Vue?"*

---

## Core Workflow

### Step 1: Normalize URL

Ensure the URL is valid and has a scheme:

```
If URL doesn't start with http:// or https:// → prepend https://
Normalize: remove trailing slash
```

### Step 2: Gather Raw Data

Use multiple techniques in parallel to collect signals:

#### 2a. HTTP Headers
```
curl -sI https://{url} 2>&1
```

Key headers to extract:
| Header | What it reveals |
|--------|----------------|
| `Server` | Nginx, Apache, Cloudflare, Caddy, Gunicorn |
| `X-Powered-By` | Express, PHP, ASP.NET, Next.js |
| `CF-Ray` / `CF-Cache-Status` | Cloudflare |
| `x-amz-*` / `x-amz-cf-*` | AWS / CloudFront |
| `x-vercel-id` | Vercel |
| `x-nuxt-*` | Nuxt.js |
| `x-robots-tag` | Often reveals framework defaults |
| `Set-Cookie` (PHPSESSID, connect.sid, etc.) | Session technology |
| `x-served-by` | Various platforms |
| `x-generator` | CMS (e.g., Drupal, Joomla) |

#### 2b. Page HTML
```
curl -sL https://{url} 2>&1
```

Inspect for:
- `<meta name="generator" content="WordPress/X.x">`
- `<script>` `src` paths containing `react`, `vue`, `angular`, `next`, `nuxt`
- `<link>` `href` containing CSS framework patterns
- `id="__next"` or `id="__nuxt"` (SSR framework markers)
- `data-*` attributes specific to frameworks
- Inline `window.__*` globals (Next.js data, Nuxt state)
- Shopify: `/cdn/shopify/`, `Shopify.shop`
- WordPress: `/wp-content/`, `/wp-json/`

#### 2c. JavaScript Globals (via Browser Console)

If browser tools are available, evaluate in page context:

```javascript
// Common framework globals
typeof React !== 'undefined'
typeof Vue !== 'undefined'
typeof angular !== 'undefined'
typeof Next !== 'undefined'
typeof Nuxt !== 'undefined'
typeof Alpine !== 'undefined'
typeof htmx !== 'undefined'
typeof jQuery !== 'undefined'
typeof Shopify !== 'undefined'
typeof Drupal !== 'undefined'

// Analytics globals
typeof ga !== 'undefined'
typeof gtag !== 'undefined'
typeof plausible !== 'undefined'
typeof umami !== 'undefined'
typeof mixpanel !== 'undefined'
typeof heap !== 'undefined'
typeof fbq !== 'undefined'  // Facebook Pixel
```

#### 2d. DNS / SSL (via terminal)
```bash
# Check DNS records
dig +short {url} A | head -5
# Check SSL certificate issuer
echo | openssl s_client -connect {url}:443 -servername {url} 2>/dev/null | openssl x509 -noout -issuer 2>/dev/null | head -5
```

#### 2e. robots.txt / sitemap (quick scan)
```
curl -sI https://{url}/robots.txt 2>&1 | head -20
```

- WordPress: often has `/wp-json/` in `robots.txt` disallows
- Static sites: minimal or no disallows

### Step 3: Analyze & Generate Report

Analyze all signals and compile a structured report.

Use this template:

```markdown
# Tech Stack Analysis: {URL}

**Date:** {YYYY-MM-DD}
**URL:** https://{url}

---

## 🏗️ Frameworks & Libraries

### Frontend Framework
- **Primary:** {React / Vue / Angular / Svelte / None detected}
- **SSR / SSG:** {Next.js / Nuxt / Astro / None}
- **Confidence:** {High / Medium / Low}
- **Evidence:** {e.g., found `__NEXT_DATA__` in HTML, or `window.React` defined}

### CSS Framework
- {Tailwind CSS / Bootstrap / Material UI / Chakra / Other / None detected}
- **Evidence:** {class name patterns, link tags}

### JavaScript Libraries
- {jQuery / Alpine.js / htmx / Three.js / D3 / None — list all detected}
- {Lib 2}
- {Lib 3}

### CMS
- {WordPress / Shopify / Sanity / Contentful / Custom / None detected}

---

## 🌐 Hosting & Infrastructure

### Hosting Provider
- **Primary:** {Vercel / Netlify / Cloudflare Pages / AWS / GCP / DigitalOcean / Dedicated server}
- **Evidence:** {headers, DNS records}

### CDN
- {Cloudflare / CloudFront / Fastly / Akamai / None detected}
- **Edge/internals:** {CF-Ray header, x-amz-cf-id, etc.}

### Web Server
- {Nginx / Apache / Caddy / Gunicorn / Node.js / Unknown}
- **Version:** {if exposed in headers}

### SSL Certificate
- **Issuer:** {Let's Encrypt / Cloudflare / DigiCert / Sectigo}
- **Expiry:** {if available}

---

## 📊 Analytics & Tracking

| Tool | Detected? | Evidence |
|------|-----------|----------|
| Google Analytics | ✅ / ❌ | `gtag` / `ga` global |
| Plausible | ✅ / ❌ | script src or global |
| Umami | ✅ / ❌ | data-website-id attribute |
| Mixpanel | ✅ / ❌ | `mixpanel` global |
| Hotjar | ✅ / ❌ | `hj` global or script |
| Facebook Pixel | ✅ / ❌ | `fbq` global |
| Heap | ✅ / ❌ | `heap` global |
| Other | ✅ / ❌ | description |

---

## ⚡ Performance & Optimization

- **HTTP/2 or HTTP/3:** {Yes / No}
- **Caching Headers:** {Aggressive / Moderate / Minimal}
- **Render-Blocking Resources:** {Count of CSS/JS in head}
- **Page Weight (estimated):** {if measurable}

---

## 🔐 Security

| Header | Status | Value |
|--------|--------|-------|
| Strict-Transport-Security | ✅ / ❌ | {value} |
| Content-Security-Policy | ✅ / ❌ | {partial/full} |
| X-Frame-Options | ✅ / ❌ | {DENY/SAMEORIGIN} |
| X-Content-Type-Options | ✅ / ❌ | {nosniff} |
| Referrer-Policy | ✅ / ❌ | {value} |

---

## 📋 Summary

| Aspect | Verdict |
|--------|---------|
| **Stack Type** | {e.g., Modern SPA / Traditional SSR / Static Site / Jamstack / Legacy} |
| **Maturity** | {Enterprise / Mid-tier / Startup / Hobby} |
| **Notable** | {Anything interesting or unusual about the tech choices} |

---

## 🔗 Sources

- HTTP headers: `curl -sI https://{url}`
- Page HTML: `curl -sL https://{url}`
- Browser console: JavaScript globals evaluation
- DNS/SSL: `dig` + `openssl` queries
- robots.txt: `curl -sI https://{url}/robots.txt`
```

---

## Detection Reference Tables

### Framework Telltales

| Framework | Detection Signal | Confidence |
|-----------|-----------------|------------|
| **React** | `id="root"` with React-rendered DOM, `__NEXT_DATA__`, `window.React` | High |
| **Next.js** | `__NEXT_DATA__` JSON script, `id="__next"`, `x-nextjs-*` header | Very High |
| **Vue** | `data-v-*` attributes on components, `window.__VUE__`, `id="app"` with Vue syntax | High |
| **Nuxt** | `__NUXT__` JSON script, `data-n-head-*`, `id="__nuxt"` | Very High |
| **Angular** | `ng-version` attribute, `_nghost-*` / `_ngcontent-*` attributes | High |
| **Svelte** | `__svelte` hash in CSS class names, `svelte-*` attributes | Medium |
| **Astro** | `astro-*` data attributes, no JS by default | High |
| **jQuery** | `window.jQuery` defined | High |
| **Alpine.js** | `x-data`, `x-init`, `x-on:*` attributes in HTML | Very High |
| **htmx** | `hx-get`, `hx-post`, `hx-trigger` attributes | Very High |

### Hosting Telltales

| Provider | Detection Signal | Confidence |
|----------|-----------------|------------|
| **Vercel** | `x-vercel-id` header, `x-vercel-cache` | Very High |
| **Netlify** | `x-nf-request-id` header, `server: Netlify` | Very High |
| **Cloudflare Pages** | `cf-ray` header + Cloudflare nameservers | High |
| **GitHub Pages** | `server: GitHub.com` | Very High |
| **AWS** | `x-amz-*` headers, `cloudfront` in CDN | High |
| **DigitalOcean** | `server: nginx` + DO DNS patterns | Medium |
| **Fly.io** | `fly-*` request ID headers | Very High |

### CDN Telltales

| CDN | Detection Signal |
|-----|-----------------|
| **Cloudflare** | `cf-ray` header, `server: cloudflare` |
| **CloudFront** | `x-amz-cf-id`, `x-amz-cf-pop` headers |
| **Fastly** | `x-served-by: cache-*`, `x-cache: HIT/MISS` |
| **Akamai** | `x-akamai-*` headers, `server: AkamaiGHost` |

---

## Example Invocations

### Example 1: Known site
```
User: What tech stack does stripe.com use?
Hermes should:
  1. Normalize URL → https://stripe.com
  2. curl -sI https://stripe.com → check headers
  3. curl -sL https://stripe.com | grep -o '<meta[^>]*generator[^>]*>' etc.
  4. Optionally open in browser to check JS globals
  5. Generate report
  6. Present to user
```

### Example 2: Unknown / small site
```
User: Analyze https://some-small-business-site.com
Hermes should:
  1. curl headers → likely shared hosting / basic setup
  2. curl HTML → check for WordPress / Shopify patterns
  3. Generate report
  4. Present findings concisely
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **No HTTPS → redirect loop.** | Use `-L` flag with curl to follow redirects. |
| 2 | **Single-page apps hide globals.** | Use browser tools to evaluate `window.*` after JS loads. |
| 3 | **Multiple frameworks possible.** | Report all detected signals with confidence levels rather than guessing. |
| 4 | **CDN obfuscates origin server.** | Check `via`, `x-cache`, `age` headers for upstream hints. Use `dig` to check origin IP. |
| 5 | **Dynamically loaded chunks.** | Browser console after 3s delay catches more lazy-loaded modules. |
| 6 | **Mixed signals (e.g., React in HTML but no global).** | Report as "React detected (SSR build — client JS not loaded)". |
| 7 | **WAF blocking curl.** | Try adding `-A "Mozilla/5.0"` user-agent. If still blocked, use browser tools. |

---

## Verification Checklist

- [ ] URL normalized (added `https://` if missing)
- [ ] HTTP headers collected and analyzed
- [ ] Page HTML scanned for framework/metadata markers
- [ ] JavaScript globals evaluated (if browser available)
- [ ] DNS/SSL checked (if terminal available)
- [ ] Hosting/CDN identified with evidence
- [ ] Analytics tools detected
- [ ] Security headers documented
- [ ] Report structured with all sections
- [ ] Confidence levels noted for each detection
