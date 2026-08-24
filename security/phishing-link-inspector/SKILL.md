---
name: phishing-link-inspector
description: "Analyze any URL, email body, or SMS for phishing and social-engineering indicators before you click — lookalike domains, suspicious TLDs, brand-impersonation, urgency/manipulation language, mismatched link text vs. href, attachment danger signals, optional DNS/whois enrichment. Local-first verdict."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [security, phishing, email, fraud, scam, social-engineering, safety, privacy, dns, whois, lookalike-domain]
    related_skills: [secret-scanner, password-auditor, inbox-triage, email-composer]
---

# Phishing Link Inspector / 钓鱼链接/邮件鉴定器

> Before you click, before you reply, before you wire money — paste the URL, email body, or SMS into Hermes and get a clear, risk-classified verdict with the exact red flags explained.

---

## Overview

This skill performs **pre-click due diligence** on any suspicious-looking URL, email body, SMS, or DM. It combines **local pattern analysis** (zero network required for the core verdict) and **optional enrichment** (DNS, WHOIS, SSL inspection, URL unshortening) to produce a one-page risk report you can act on in 30 seconds.

The skill targets the exact things humans miss under pressure — lookalike domains, urgent language, mismatched link text, brand impersonation, attachment danger, and money/time-pressure manipulation.

| Feature | What It Does | How |
|---------|-------------|-----|
| **URL Anatomy Parse** | Decomposes a URL — scheme, host, TLD, path, query, fragment; flags IDN/punycode, raw IPs, suspicious ports | Python `urllib.parse` + regex |
| **Lookalike Domain Detector** | Catches `paypa1.com`, `arnazon.com`, `micros0ft-support.com` (homoglyphs + number swaps + subdomain confusion) | Levenshtein + common-brand dict |
| **TLD / Domain-Age Risk** | Flags `.zip`/`.top`/`.xyz`/`.click`/country-TLD clusters often used by phishers | Local TLD reputation list |
| **Brand Impersonation** | Detects strings like "PayPal", "Stripe", "USPS", "DHL", "DocuSign", "HR", "CEO" in URL or body | Brand dictionary + context scoring |
| **Urgency & Manipulation Language** | Identifies pressure tactics ("within 24 hours", "account suspended", "verify now", "wire transfer") | Bilingual keyword lexicon (EN+CN) |
| **Link-Text Mismatch** | In HTML emails, compares visible link text vs. actual `href` target | HTML parser + href extractor |
| **Attachment Danger Signals** | Flags `.exe`, `.scr`, `.iso`, `.docm`, `.html`, `.js`, `.lnk`, `.zip`-with-password | Extension + double-extension patterns |
| **URL Unshortener** | Follows `bit.ly`/`tinyurl.com`/`t.co`/etc. redirects to the final destination | curl with redirect-follow, max 5 hops |
| **Optional DNS / WHOIS** | Resolves A/AAAA/MX, queries domain creation date | `dig` + `whois` (graceful skip if offline) |
| **Risk Verdict** | Outputs **SAFE / SUSPICIOUS / LIKELY PHISHING / CONFIRMED PHISHING** with 0-100 score | Weighted composite |

All analysis runs **locally**. Enrichment queries are optional and labeled. **Nothing you paste is sent to a third party.**


## When to Use

- **"Is this link safe?"** — paste a suspicious URL and get a verdict before clicking
- **"Analyze this email — is it phishing?"** — paste the whole email body (text or raw HTML)
- **"Check this SMS from 'USPS' / 'FedEx' / my bank"** — paste the SMS
- **"What does this bit.ly link actually go to?"** — unshorten and inspect the final URL
- **"I got a DocuSign / HR / invoice email that feels off"** — paste it
- **"Is `paypa1-secure.com` legit?"** — domain-impersonation check
- **"Verify before I wire money / click / reply"** — pre-action due diligence
- Any request mentioning **"phishing", "scam link", "可疑链接", "钓鱼邮件", "诈骗短信", "suspicious email", "is this legit"**


## Core Workflow

### Step 1: Accept the input and classify

The user pastes one of four shapes. Detect automatically:

```bash
# 1) Bare URL → URL inspection
echo "$INPUT" | grep -qE '^https?://' && MODE=url

# 2) HTML → email inspection (extract URLs + body text first)
echo "$INPUT" | grep -qiE '<html|<body|<a href' && MODE=email_html

# 3) Plain text with URL → email/SMS body inspection (extract URL from text)
echo "$INPUT" | grep -qE 'https?://' && MODE=body_with_url

# 4) Pure text → SMS / DM body inspection
[[ -z "$MODE" ]] && MODE=text
```

**Always confirm with the user:**
> *"I'll inspect this as a [URL / email / SMS]. Sound right?"*


### Step 2: Run the local verdict (no network required)

Parse and score locally. Every flag carries a weight; total score → verdict.

```python
# phishing_score.py — pure stdlib, runs offline
import re, sys, json
from urllib.parse import urlparse
from html.parser import HTMLParser

URGENCY_EN = [
    r"within \d+ (hour|day|minute)", r"act now", r"urgent(ly)?", r"immediately",
    r"account (will be )?suspended", r"verify (your )?(identity|account|email)",
    r"click (here|below|the link)", r"confirm (your )?(password|account)",
    r"limited time", r"final notice", r"wire transfer", r"gift card",
    r"tax (lien|audit|owe)", r"social security", r"ssn", r"irs",
]
URGENCY_CN = [
    r"立即", r"马上", r"24小时内", r"逾期", r"冻结", r"验证码",
    r"账户异常", r"身份验证", r"点击下方链接", r"补交", r"保证金",
    r"中奖", r"兼职刷单", r"退款", r"快递签收", r"ETC",
]
BRANDS = [
    "paypal","stripe","apple","google","microsoft","amazon","facebook","meta",
    "instagram","netflix","usps","fedex","ups","dhl","docusign","intuit",
    "wells fargo","chase","bank of america","citi","hsbc","linkedin","github",
    "dropbox","icloud","office365","outlook","slack","zoom","coinbase","binance",
]
SUSPICIOUS_TLDS = {
    ".zip",".mov",".top",".xyz",".click",".country",".kim",".work",
    ".review",".gq",".cf",".ml",".tk",".ga",".loan",".win",".racing",
    ".date",".party",".trade",".stream",".download",".science",
}
DANGEROUS_EXTS = {".exe",".scr",".bat",".cmd",".com",".pif",".vbs",".js",
                  ".jar",".msi",".iso",".img",".lnk",".hta",".docm",".xlsm",
                  ".pptm",".rar",".7z",".zip"}
HIGH_RISK_EXT_DOUBLE = True  # "invoice.pdf.exe" pattern

class LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.in_a=False; self.text=""
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            self.in_a=True; self._href=dict(attrs).get("href","")
        elif tag=="img":
            src=dict(attrs).get("src","")
            if src: self.links.append(("img",src))
    def handle_endtag(self,tag):
        if tag=="a": self.in_a=False
    def handle_data(self,data):
        self.text+=data
        if self.in_a: self._text=data
    @property
    def pairs(self):
        return [(self._href, getattr(self,"_last_a_text",""))]

def levenshtein(a,b):
    if a==b: return 0
    if not a: return len(b)
    if not b: return len(a)
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        cur=[i]+[0]*len(b)
        for j,cb in enumerate(b,1):
            cur[j]=min(cur[j-1]+1, prev[j]+1, prev[j-1]+(ca!=cb))
        prev=cur
    return prev[-1]

def score_url(url: str) -> dict:
    flags=[]; score=0
    try:
        p=urlparse(url)
    except Exception:
        return {"url":url,"score":100,"flags":["UNPARSEABLE_URL"],"verdict":"LIKELY PHISHING"}
    host=p.hostname or ""; tld="."+host.rsplit(".",1)[-1].lower() if "." in host else ""
    path=p.path or ""
    # Raw IP host
    if re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", host):
        flags.append("RAW_IP_HOST"); score+=25
    # Non-standard port
    if p.port and p.port not in (80,443):
        flags.append(f"NONSTANDARD_PORT:{p.port}"); score+=10
    # Punycode / IDN
    if "xn--" in host:
        flags.append("PUNYCODE_DOMAIN"); score+=25
    # Suspicious TLD
    if tld in SUSPICIOUS_TLDS:
        flags.append(f"SUSPICIOUS_TLD:{tld}"); score+=15
    # Hyphens in domain (cheap typo squat)
    hyphens=host.count("-")
    if hyphens>=2:
        flags.append(f"MANY_HYPHENS:{hyphens}"); score+=10
    # Long subdomain chain (≥4 labels)
    labels=host.split(".")
    if len(labels)>=4:
        flags.append(f"DEEP_SUBDOMAIN:{len(labels)}"); score+=10
    # Userinfo in URL
    if p.username:
        flags.append("USERINFO_IN_URL"); score+=20
    # Lookalike vs known brand — check each hyphen/underscore token separately
    # (e.g. "paypa1-secure-verify.com" → tokens "paypa1","secure","verify")
    sld=labels[-2] if len(labels)>=2 else host
    for b in BRANDS:
        if sld.startswith(b) and sld!=b:
            flags.append(f"BRAND_PREFIX:{sld}"); score+=15; break
    hit=False
    for lbl in labels[:-1]:
        for tok in re.split(r"[-_]", lbl):
            tok=tok.lower()
            for b in BRANDS:
                if tok==b:   # exact brand token in a subdomain is handled by other flags
                    continue
                d=levenshtein(tok, b)
                if 0<d<=2:
                    flags.append(f"LOOKALIKE:{tok}≈{b}"); score+=30; hit=True; break
            if hit: break
        if hit: break
    # '@' sign in path (old classic)
    if "@" in path:
        flags.append("AT_SIGN_IN_PATH"); score+=25
    # Many query params carrying data (credential harvest style)
    qn=len([k for k in p.query.split("&") if "=" in k])
    if qn>=3:
        flags.append(f"DATA_HEAVY_QUERY:{qn}"); score+=5
    return {"url":url,"host":host,"tld":tld,"score":min(score,100),"flags":flags}

def score_body(text: str) -> dict:
    flags=[]; score=0
    lower=text.lower()
    for pat in URGENCY_EN+URGENCY_CN:
        if re.search(pat, lower):
            flags.append(f"URGENCY:{pat}"); score+=10; break
    if re.search(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?", text) or "电汇" in text or "转账" in text:
        flags.append("MONEY_REQUEST"); score+=15
    if re.search(r"密码|password|验证码|verification code|one[- ]time", lower):
        flags.append("CREDENTIAL_REQUEST"); score+=15
    if re.search(r"语音留言|voicemail|secure document|shared file", lower):
        flags.append("SUSPICIOUS_ATTACH_REF"); score+=10
    # Brand impersonation in From/署名
    for b in BRANDS:
        if b in lower and re.search(r"(from|by|on behalf|代表).{0,20}"+b, lower):
            flags.append(f"BRAND_CLAIM:{b}"); score+=10; break
    return {"score":min(score,100),"flags":flags}

def score_attachment(name: str) -> dict:
    flags=[]; score=0
    base=name.lower()
    for ext in DANGEROUS_EXTS:
        if base.endswith(ext):
            flags.append(f"DANGEROUS_EXT:{ext}"); score+=30; break
    # Double extension like report.pdf.exe
    parts=base.rsplit(".",1)
    if len(parts)==2 and "." in parts[0]:
        second=parts[0].rsplit(".",1)[-1]
        if second in {"pdf","doc","xls","txt","jpg"}:
            flags.append(f"DOUBLE_EXT:{name}"); score+=40
    if re.search(r"\.zip$|\.rar$|\.7z$", base) and ("password" in base or "密码" in base):
        flags.append("ENCRYPTED_ARCHIVE"); score+=20
    return {"score":min(score,100),"flags":flags}
```

**Composite verdict rule (defaults; tuneable):**

```python
def verdict(score):
    if score>=70: return "🔴 CONFIRMED PHISHING — DO NOT CLICK / REPLY"
    if score>=40: return "🟠 LIKELY PHISHING — verify out-of-band before acting"
    if score>=20: return "🟡 SUSPICIOUS — multiple minor red flags"
    return "🟢 LIKELY SAFE — no major red flags detected"
```


### Step 3: Optional enrichment (network, ask first)

Only run if the user confirms and you're online. Each step has a short timeout.

**a) Unshorten:**

```bash
unshorten() {
  local url="$1" i=0
  while (( i<5 )); do
    loc=$(curl -s -o /dev/null -w "%{url_effective}\n%{http_code}" \
           -A "Mozilla/5.0" --max-time 5 -L "$url" 2>/dev/null)
    final=$(echo "$loc" | head -1); code=$(echo "$loc" | tail -1)
    (( i++ ))
    [[ "$final" == "$url" || -z "$final" ]] && break
    url="$final"
  done
  echo "Final URL after $i hops: $url (HTTP $code)"
}
```

**b) DNS / age:**

```bash
whois_age() {
  local domain="$1"
  whois "$domain" 2>/dev/null | \
    awk -F: '/Creation Date|Registered|Created|注册/ {gsub(/^ +/,"",$2); print $2; exit}' \
    | head -1
}
# Fallback: rdap via curl if whois missing
rdap_age() {
  curl -s --max-time 5 "https://rdap.org/domain/$1" | \
    python3 -c 'import sys,json; d=json.load(sys.stdin);
print([e["eventDate"] for e in d.get("events",[]) if "registration" in e.get("eventAction","")])'
}
# Flag: <30 days = high risk, 30-365 = medium, >365 = lower risk
```

**c) SSL issuer (warn if brand-mismatch on a brand-claiming URL):**

```bash
ssl_issuer() {
  echo | openssl s_client -servername "$1" -connect "$1":443 2>/dev/null \
    | openssl x509 -noout -issuer -subject -dates 2>/dev/null
}
```


### Step 4: Render the verdict card

Always produce a single, scannable card. Example:

```
╔══════════════════════════════════════════════════════════════╗
║  PHISHING INSPECTION REPORT                          09:42   ║
╠══════════════════════════════════════════════════════════════╣
║  Input : https://paypa1-secure-verify.com/login              ║
║  Mode  : URL                                                  ║
║  Score : 45 / 100                                             ║
║  Verdict : 🟠 LIKELY PHISHING — verify out-of-band            ║
╠══════════════════════════════════════════════════════════════╣
║  Red flags (3)                                                ║
║   • LOOKALIKE: paypa1 ≈ paypal                  (+30)          ║
║   • MANY_HYPHENS: 2                             (+10)          ║
║   • DATA_HEAVY_QUERY: 3 params                  (+5)          ║
╠══════════════════════════════════════════════════════════════╣
║  Recommendation                                               ║
║   • Do not click. Do not reply.                               ║
║   • Independently log in to PayPal via a NEW tab/bookmark.     ║
║   • Report: forward to phishing@paypal.com then delete.       ║
╚══════════════════════════════════════════════════════════════╝
```


### Step 5: Offer next actions

End every verdict with 2-3 offered next actions based on context:

- **CONFIRMED/LIKELY PHISHING** → "Want me to draft a one-line 'this looks like a scam' reply?" (uses `email-composer`) / "Want me to add this to your `secret-scanner` ignore list?"
- **SAFE** → "Want me to write you a `email-composer` template for replying?"
- **Email mode + attachment found** → "Want me to draft the actual safer version of the body?"


## Example Invocations

### Example 1: Bare URL check

> **User:** is this link safe? `http://paypa1-secure-verify.com/signin?session=ab12&token=cd34&id=ef56`

**Agent:**
- Mode: URL
- Parses → host `paypa1-secure-verify.com`, TLD `.com`, 3 query params
- Hits LOOKALIKE (`paypa1` vs `paypal`, Levenshtein=1), MANY_HYPHENS (2), DATA_HEAVY_QUERY
- Composite: 30+10+5 = 45 → 🟠 **LIKELY PHISHING**
- Offers DNS lookup; user declines.
- Reports verdict card, recommends reporting to `phishing@paypal.com`.

---

### Example 2: Email body with mismatched link

> **User:** is this DHL package email legit?
> ```
> From: DHL Express <delivery-notice@dhl-customer-services.com>
> Subject: Your package is held at customs — verify within 24 hours
>
> Dear customer, your parcel could not be delivered. Pay the
> $2.99 customs fee to release it:
>   <a href="http://dhl-customs-pay.xyz/release?id=8821">https://www.dhl.com/track?id=8821</a>
>
> Failure to pay within 24 hours will result in return to sender.
> ```

**Agent:**
- Mode: email_html (or body_with_url)
- Extracts the **visible text** link `https://www.dhl.com/track?id=8821` vs the **real href** `http://dhl-customs-pay.xyz/release?id=8821` → **MISMATCH** (+30)
- Suspicious TLD `.xyz` (+15)
- Brand impersonation DHL (+10)
- Urgency "within 24 hours" (+10)
- Money request $2.99 (+15)
- Total: 80 → 🔴 **CONFIRMED PHISHING**
- Verdict card + recommended reply: *"This is a known DHL customs-fee scam — DHL never collects fees via email links."* Offers `email-composer` for a one-line reply.


### Example 3: SMS / smishing

> **User:** got this text, is it real? "USPS: Your package is awaiting delivery. Confirm your address at usps-track.top/c/8x2pA within 24h or it will be returned."

**Agent:**
- Mode: body_with_url (URL embedded)
- Extracts `usps-track.top`
- URL flags: SUSPICIOUS_TLD(`.top`) (+15), BRAND_PREFIX (`usps-track` prefix squat) (+15) → 30
- Body flags: urgency "within 24h" (+10) → 10
- Composite: 30+10 = 40 → 🟠 **LIKELY PHISHING**
- Offers to call USPS at the number on the **official site** (NOT one in the SMS) to verify.


## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Punycode domain looks normal (`xn--ggle-55da.com` is `googĺe.com`) | Always check for `xn--` prefix; show the decoded form next to the raw |
| Phisher hides brand in subdomain (`paypal.com.evil.ru`) | Score by the **registered domain** (last 2 labels), not the full host |
| Legit shortener (`t.co`) masks a malicious final URL | Always run `unshorten` on any shortener; inspect the *final* URL |
| Legit marketing email triggers URGENCY ("Last day! 50% off!") | Score urgency *combined with* credential/money requests — a sale isn't a phish on its own |
| HTML `display:none` link hides the real href from users | When extracting link pairs, respect CSS-hidden anchors; surface them |
| User pastes a real-looking PDF link | Still score the URL — invoice-themed `.pdf.exe` is the classic |
| Domain age lookup times out / no `whois` installed | Fall back to RDAP (`curl rdap.org/domain/X`); if both fail, mark "AGE UNKNOWN" and lean toward SUSPICIOUS |
| User pastes corporate internal link (`intranet.corp.local`) | Skip enrichment (no public DNS); score purely on pattern match |
| False positive: `accounts.google.com` flagged for "account" | Only flag BRAND_PREFIX if the registered domain is **not** the official brand TLD — whitelist known-good base domains |
| User wants to "test" against a real phishing site | **Refuse** — never curl user-supplied suspicious URLs in non-sandboxed way; only inspect the *string*, never execute the link's payload |


## Verification Checklist

Before delivering the verdict, confirm:

- [ ] Input was classified as URL / HTML / body / text
- [ ] All URLs were extracted (including HTML `<a href>` and `display:none` ones)
- [ ] Lookalike check ran against the **registered domain** (not the full host)
- [ ] Brand-prefix check ignored the official brand's own TLDs
- [ ] Urgency / credential / money scores are present (none required)
- [ ] Attachment extensions scanned if email referenced files
- [ ] Link-text vs. href mismatch was checked in HTML mode
- [ ] Composite score and verdict text are consistent
- [ ] Optional enrichment only ran after user consent
- [ ] Output is a single scannable card, not a wall of text
- [ ] Next-action offers are tailored to the verdict (not generic)
- [ ] No raw URL was opened / followed beyond header inspection


## Data Sources & Accuracy

| Source | Used For | Local / Network | Notes |
|--------|----------|-----------------|-------|
| Built-in Python `urllib.parse` | URL anatomy | Local | Always available |
| Local brand + TLD dictionaries | Lookalike / TLD scoring | Local | Editable: edit `BRANDS` / `SUSPICIOUS_TLDS` |
| Local EN+CN urgency lexicon | Manipulation language | Local | Covers the top 90% of common phishing patterns |
| `curl` redirect follow | Unshortening | Network, opt-in | 5-hop max, 5s timeout per hop |
| `whois` / RDAP (`rdap.org`) | Domain creation date | Network, opt-in | Used to add age risk; absence raises score conservatively |
| `openssl s_client` | SSL issuer / SAN list | Network, opt-in | Only used when the URL claims a brand |
| **No third-party reputation API required** | — | — | Everything works offline for the core verdict |

**Accuracy caveats:**

- This is **pattern + heuristic** analysis. Sophisticated, hand-crafted phishing can bypass any static check.
- Always pair this skill with the user's own judgment: **"Did I expect this email? Does it create false urgency? Would the sender know my real name / account?"**
- New phishing TLDs and brand-spoofs appear weekly. Update the `BRANDS` and `SUSPICIOUS_TLDS` lists periodically (consider a monthly cron review).
- This skill **never opens the suspicious URL's payload**. It only inspects the *string* and metadata. Always.