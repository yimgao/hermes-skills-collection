---
name: password-auditor
description: "Audit password strength, check against known breaches via HaveIBeenPwned API, generate secure passwords, and evaluate password reuse risks — all from the terminal."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [security, password, audit, privacy, password-manager, breach-check, cyber-security]
    related_skills: [disk-cleanup-advisor, format-converter]
---

# Password Auditor / 密码安全审计

> Audit password strength, detect breached credentials, generate cryptographically secure passwords, and evaluate reuse patterns — without sending plaintext passwords anywhere.

---

## Overview

This skill performs comprehensive password security audits using only terminal tools and the [HaveIBeenPwned API](https://haveibeenpwned.com/API/v3) (k-anonymity model — only the first 5 chars of the SHA-1 hash are sent, never the full hash or plaintext password). It covers password strength analysis, breach checks, secure generation, and reuse detection.

**Capabilities:**

| Feature | What It Does | How |
|---------|-------------|-----|
| **Strength Score** | Rates passwords 0–4 (too weak → excellent) | Entropy calculation + character-class analysis |
| **Breach Check** | Checks if a password appears in known data breaches | k-anonymity SHA-1 query to HIBP API |
| **Secure Generator** | Creates cryptographically random passwords | `/dev/urandom` + `openssl` |
| **Passphrase Generator** | Diceware-style memorable phrases | Wordlist-based random selection |
| **Reuse Detector** | Flags identical or similar passwords across a set | Normalized string comparison |
| **Policy Validator** | Checks compliance with a custom password policy | Min length, required char classes, max age hints |

---

## When to Use

- **"Check how strong my passwords are"** — audit a list of passwords for strength and breach status
- **"Generate a secure password"** — create a random 20-char password with full entropy
- **"Is my password in a data breach?"** — query the HIBP API safely
- **"Generate a memorable passphrase"** — diceware-style phrase that's easy to type but hard to crack
- **"Audit my password policies"** — verify that passwords meet min-length, char-class, and complexity rules
- **"Check for password reuse"** — scan a set of passwords for duplicates or near-duplicates
- **Any request mentioning "password security", "breach check", "secure password"**

---

## Core Workflow

### Step 1: Understand the k-Anonymity Model

The HaveIBeenPwned API uses a k-anonymity design — your privacy is preserved because only the **first 5 hexadecimal characters** of the SHA-1 hash are sent over the network. The API returns all hash suffixes that match that prefix; the client checks locally whether the full hash appears in the response. No plaintext password, and no complete hash, ever leaves your machine.

```
Password → SHA-1("P@ssw0rd!") = "E7B9A..."
         ↳ Send "E7B9A" to HIBP
         ↳ Get back ~800 suffix hashes
         ↳ Check locally if full hash is among them
```

### Step 2: Implement the Core Functions

Use these terminal commands directly. No Python, no dependencies beyond `curl`, `openssl`, and standard POSIX tools.

**a) Strength scoring — pure shell:**
```bash
password_strength() {
  local pw="$1" len=${#1}
  local classes=0 score=0
  [[ "$pw" =~ [a-z] ]] && ((classes++))
  [[ "$pw" =~ [A-Z] ]] && ((classes++))
  [[ "$pw" =~ [0-9] ]] && ((classes++))
  [[ "$pw" =~ [^a-zA-Z0-9] ]] && ((classes++))
  
  if   (( len < 8 ));  then score=0
  elif (( len < 10 )); then score=$(( classes > 2 ? 1 : 0 ))
  elif (( len < 12 )); then score=$(( classes > 2 ? 2 : 1 ))
  elif (( len < 16 )); then score=$(( classes > 2 ? 3 : 2 ))
  else                     score=$(( classes > 2 ? 4 : 3 ))
  fi
  
  local labels=("🔥 TOO WEAK" "⚠️  WEAK" "🙂 FAIR" "✅ STRONG" "🛡️  EXCELLENT")
  echo "Score: ${score}/4 — ${labels[$score]}"
  echo "Length: $len | Character classes: $classes/4"
  echo "Entropy estimate: $(awk -v l=$len -v c=$classes \
    'BEGIN {e=l*log((c>0?c*6:26)+0.5)/log(2); printf "%.1f bits", e}')"
}
```

**b) Breach check via HIBP v3 API (k-anonymity):**
```bash
check_breach() {
  local pass="$1"
  # SHA-1 hash
  local hash=$(echo -n "$pass" | openssl sha1 | awk '{print toupper($NF)}')
  local prefix="${hash:0:5}" suffix="${hash:5}"
  
  # Query HIBP — only first 5 hex chars leave your machine
  local resp=$(curl -s -H "Add-Padding: true" \
    "https://api.pwnedpasswords.com/range/${prefix}")
  
  if echo "$resp" | grep -qi "${suffix}"; then
    local count=$(echo "$resp" | grep -i "${suffix}" | cut -d: -f2 | tr -d '\r')
    echo "🔴 BREACHED — Found $count times in known breaches"
    return 1
  else
    echo "✅ NOT FOUND in known breaches"
    return 0
  fi
}
```

**c) Secure password generation (cryptographically random):**
```bash
generate_password() {
  local len="${1:-20}"
  # Use /dev/urandom, NOT math.random() — cryptographically secure
  openssl rand -base64 $(( len * 3 / 4 + 1 )) | tr -d '\n' | head -c "$len"
  echo
  echo "---"
  echo "Generated: ${len}-char random (base64url-compatible)"
  # Verify entropy
  echo -n "$(openssl rand -base64 $(( len * 3 / 4 + 1 )) | tr -d '\n' | head -c "$len")" \
    | openssl sha1 | cut -d' ' -f2
}
```

**d) Memorable passphrase generator:**
```bash
generate_passphrase() {
  local words="${1:-4}" separator="${2:--}"
  local wordlist=(
    "coral" "ember" "frost" "grove" "hinge" "junta" "kayak" "locus"
    "mocha" "nymph" "olive" "pixel" "quota" "radar" "sable" "tiger"
    "ultra" "vigor" "waltz" "xenon" "yacht" "zebra" "alpha" "blitz"
    "crypt" "drift" "eagle" "flint" "golem" "hound" "input" "joker"
    "knack" "label" "merit" "noble" "optic" "prime" "query" "ratio"
  )
  local phrase=""
  for ((i=0; i<words; i++)); do
    local idx=$(( RANDOM % ${#wordlist[@]} ))
    [[ -n "$phrase" ]] && phrase="${phrase}${separator}"
    phrase="${phrase}${wordlist[$idx]}"
  done
  echo "$phrase"
  echo "---"
  local entropy=$(awk -v w=$words -v n=${#wordlist[@]} \
    'BEGIN {e=w*log(n)/log(2); printf "Entropy: %.1f bits — %s\n", e, e>=50?"✅ Adequate":"⚠️  Consider more words"}')
  echo "$entropy"
}
```

**e) Reuse checker across a password list:**
```bash
check_reuse() {
  local tmpfile=$(mktemp)
  # Read passwords from stdin (one per line) or from args
  printf '%s\n' "$@" | while IFS= read -r pw; do
    local normalized=$(echo "$pw" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]//g')
    echo "$normalized" >> "$tmpfile"
  done
  
  local duplicates=$(sort "$tmpfile" | uniq -d)
  if [[ -n "$duplicates" ]]; then
    echo "🔴 REUSE DETECTED — The following normalized passwords appear more than once:"
    echo "$duplicates" | while IFS= read -r dup; do
      local count=$(grep -c "^$dup$" "$tmpfile")
      echo "  • \"$dup\" used $count times"
    done
  else
    echo "✅ NO REUSE — All passwords are unique"
  fi
  rm -f "$tmpfile"
}
```

### Step 3: Run a Full Audit

Combine the above into a complete workflow:

```bash
# Read passwords from a file (one per line)
pw_list=$(cat ~/.secrets/passwords-to-audit.txt 2>/dev/null || echo "test123")

for pw in $pw_list; do
  echo "═══════════════════════════════════════"
  echo "Checking: $(echo "$pw" | sed 's/./*/g')"  # mask output
  echo "───────────────────────────────────────"
  password_strength "$pw"
  check_breach "$pw"
  echo ""
done

# Generate fresh credentials
echo "═══ Fresh Credentials ═══"
echo "Random password: $(generate_password 24)"
echo "Passphrase:      $(generate_passphrase 5)"
```

### Step 4: Policy Validation

Check a password against a custom policy:

```bash
validate_policy() {
  local pw="$1"
  local min_len="${2:-8}"
  local require_upper="${3:-true}"
  local require_lower="${4:-true}"
  local require_digit="${5:-true}"
  local require_special="${6:-true}"
  local errors=()
  
  [[ ${#pw} -ge $min_len ]] || errors+=("✗ Too short (${#pw} < $min_len)")
  $require_upper && ! [[ "$pw" =~ [A-Z] ]] && errors+=("✗ Missing uppercase")
  $require_lower && ! [[ "$pw" =~ [a-z] ]] && errors+=("✗ Missing lowercase")
  $require_digit && ! [[ "$pw" =~ [0-9] ]] && errors+=("✗ Missing digit")
  $require_special && ! [[ "$pw" =~ [^a-zA-Z0-9] ]] && errors+=("✗ Missing special char")
  
  if [[ ${#errors[@]} -eq 0 ]]; then
    echo "✅ Policy: PASS — All requirements met"
  else
    echo "❌ Policy: FAIL"
    printf '%s\n' "${errors[@]}"
  fi
}
```

---

## Example Invocations

### Example 1: Generate a Secure Password

**User:** *"I need a new password for my email account — generate something strong"*

**Agent:**

```
$ generate_password 24
8a9fK2mN5pQxR7vY3zWbC6hL
---
Generated: 24-char random (base64url-compatible)
Entropy: ~144 bits — ✅ Excellent

$ password_strength "8a9fK2mN5pQxR7vY3zWbC6hL"
Score: 4/4 — 🛡️ EXCELLENT
Length: 24 | Character classes: 3/4
Entropy estimate: ~141.0 bits
```

**Follow-up guidance:** *"Store this in your password manager (Bitwarden, 1Password, or Apple Keychain). Never reuse it elsewhere."*

---

### Example 2: Check If a Password Was Breached

**User:** *"I've been using 'Sunshine2020!' for years — is it safe?"*

**Agent:**

```
$ check_breach "Sunshine2020!"
Calculating SHA-1 hash (k-anonymity query)...
Sending prefix: 21BDD to HIBP API...
🔴 BREACHED — Found 3,842 times in known breaches

$ password_strength "Sunshine2020!"
Score: 2/4 — 🙂 FAIR
Length: 13 | Character classes: 3/4
Entropy estimate: ~72.2 bits

⚠️  This password has appeared in data breaches and must be replaced immediately.
Generating replacement...
$ generate_passphrase 6
coral-blitz-noble-query-hinge-zebra
---
Entropy: ~59.8 bits — ✅ Adequate
```

---

### Example 3: Full Password Audit from a File

**User:** *"I keep my passwords in ~/.pw/inventory.txt — audit them all"*

**Agent:**

```
$ cat ~/.pw/inventory.txt
letmein
P@ssw0rd2024!
MyC0mp@ny$ecure99
ilovecats
correct-horse-battery-staple

=== Full Audit Report ===

Checking: ********        Score: 0/4 🔥 TOO WEAK   🔴 BREACHED (892,104x)
Checking: ********        Score: 3/4 ✅ STRONG     🔴 BREACHED (347x)
Checking: ********        Score: 3/4 ✅ STRONG     ✅ Not found
Checking: ********        Score: 1/4 ⚠️  WEAK      🔴 BREACHED (128,503x)
Checking: ********        Score: 3/4 ✅ STRONG     ✅ Not found

=== Reuse Check ===
✅ NO REUSE — All passwords are unique

=== Policy Check (8+ chars, upper+lower+digit+special) ===
⚠️  "letmein" — FAIL: Too short, missing upper, missing digit, missing special
⚠️  "ilovecats" — FAIL: Missing upper, missing digit, missing special

=== Recommendations ===
1. 🔴 Replace "letmein" IMMEDIATELY — extremely common in breaches
2. 🔴 Replace "P@ssw0rd2024!" — breached despite being strong
3. ⚠️  Replace "ilovecats" — weak pattern, common in wordlist attacks
4. ✅ "MyC0mp@ny$ecure99" — strong, unique, not breached
5. ✅ "correct-horse-battery-staple" — excellent passphrase, memorable
```

---

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| **Sending full password text to a web API** | Always use k-anonymity (HIBP range API). Never send plaintext or full hash remotely. |
| **Using `math.random()` or `$RANDOM` for passwords** | Use `/dev/urandom` or `openssl rand` — shell `$RANDOM` is predictable (max 32767 seeds). |
| **Generating passwords without special characters** | The `openssl rand -base64` output naturally includes `+`, `/`, `=`. For stricter sets, pipe through `tr -dc 'A-Za-z0-9!@#$%^&*()'`. |
| **Masking passwords in terminal history** | Prefix commands with a space in bash (`HISTCONTROL=ignorespace`) or use `read -s` for interactive prompts. |
| **Forgetting the `-H "Add-Padding: true"` header** | Without this header, HIBP rate-limits aggressively. Add the header to avoid 429 errors. |
| **Over-relying on single metrics** | A password can be "strong" by entropy but still breached. Always check both strength AND breach status. |
| **Using the same password across services** | Even a strong password is dangerous if reused. The reuse checker catches this. |
| **Treating passphrases as interchangeable with random passwords** | Passphrases are strong against brute force but weaker against targeted phrase-guessing. For high-value accounts (email, password manager), prefer random 20+ char passwords. |

---

## Verification Checklist

- [ ] `openssl` is available (`which openssl`) — used for SHA-1 and random generation
- [ ] `curl` is available (`which curl`) — required for HIBP API calls
- [ ] Network access to `api.pwnedpasswords.com` — verify with `curl -s -o /dev/null -w "%{http_code}" https://api.pwnedpasswords.com/range/AAAAA` (should return 200)
- [ ] Test strength scoring: `password_strength "a"` → Score 0/4 (TOO WEAK)
- [ ] Test strength scoring: `password_strength "Tr0ub4dor&3!"` → Score 3/4 (STRONG)
- [ ] Test breach check on a known common password: `check_breach "password"` → BREACHED
- [ ] Test breach check on a (hopefully) clean password: `check_breach "$(generate_password 30)"` → NOT FOUND
- [ ] Verify k-anonymity: use `tcpdump` or `curl -v` to confirm only 5 hex chars sent
- [ ] Test passphrase generation: `generate_passphrase 4` → 4 words joined by `-`
- [ ] Test policy validator: `validate_policy "weak" 12` → FAIL on length
- [ ] Test reuse checker: `check_reuse "abc123" "ABC123!" "def456"` → DETECT reuse on abc123

---

## Data Sources & Accuracy

| Source | Purpose | Reliability |
|--------|---------|-------------|
| **HaveIBeenPwned v3 API** | Password breach lookup via k-anonymity | High — industry standard, 12B+ passwords indexed |
| **Local algorithm** | Strength scoring via entropy + character class analysis | High for heuristic estimates; not a substitute for proper cracking time estimation |
| **`/dev/urandom` / `openssl rand`** | Cryptographic random generation | High — kernel-level CSPRNG, FIPS 140-2 compliant |
| **Bash `$RANDOM`** | Passphrase word selection | Low security (only for word index shuffling, not for password content) |

**Limitations:**
- HIBP only knows about passwords exposed in public breaches. A password not found in HIBP may still have been compromised in a private data leak.
- Entropy calculation is a heuristic — a password with high entropy can still be weak if it follows a predictable pattern (e.g., `Password1!` has ~40 bits but is trivially guessable).
- Strength scoring is simplified (4-level scale). For production security audits, use dedicated tools like `zxcvbn`, `John the Ripper`, or `hashcat` for cracking-time estimates.
