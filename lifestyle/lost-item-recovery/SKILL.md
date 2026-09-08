---
name: lost-item-recovery
description: "Use when something important is lost or stolen — passport, wallet, phone, laptop, luggage, keys, car, package, even a pet. Walks you through the exact emergency steps in the right order: secure-the-rest, find-my-device, file police report, contact issuers, freeze cards, replace IDs, claim insurance, dispute charges. Adapts to your country and current location. Pairs with renewal-reminder for replacing expiring IDs and travel-itinerary-planner for trip context."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [lost, stolen, recovery, wallet, passport, phone, laptop, luggage, keys, fraud, identity-theft, emergency, travel-emergency, insurance-claim, dispute, find-my-device, freeze-cards, police-report]
    related_skills: [renewal-reminder, travel-itinerary-planner, personal-crm, car-maintenance-tracker, medical-visit-companion, phishing-link-inspector, secret-scanner, subscription-manager, investment-portfolio-tracker]
---

# 🆘 Lost Item Recovery — 失物/失窃应急响应

> When something important is gone — your passport before a flight, your wallet on a trip, your phone in a cab, your dog at the park — don't panic and don't guess. Tell Hermes what was lost, where, and your situation, and get the **exact ordered checklist** of what to do in the next 5 minutes, the next hour, and the next 3 days, with the phone numbers, app links, and replacement form URLs you actually need.

---

## Overview

This skill is an **emergency triage + recovery playbook** for lost or stolen items. It produces a time-stamped, situation-specific action plan — not generic advice. It answers the questions that matter most in the first hour:

1. **What should I do *right now* (next 5 minutes)?** — secure the rest of your life first
2. **How do I find / locate it?** — which Find-My app, which carrier, which airline desk
3. **What do I freeze, cancel, or report?** — banks, cards, carriers, IDs, accounts
4. **What documents do I need to replace it?** — which office, which form, which fees
5. **Will insurance / travel insurance / homeowner cover it?** — claim playbook
6. **How do I dispute fraudulent charges if the worst happened?** — FCRA / Fair Credit Billing steps

The skill pairs naturally with:
- **`renewal-reminder`** — to schedule re-issued IDs, replacement passports, new insurance cards
- **`travel-itinerary-planner`** — to understand trip context, embassy/ consulate hours, language barriers
- **`personal-crm`** — to know who you may need to contact (hotel concierge, airline agent, embassy contacts)
- **`phishing-link-inspector`** — to vet any "we found your item, click here" follow-up scam

All recovery steps are **country-aware** (US, UK, EU, China, JP, generic) and **item-aware** (each item has its own runbook). Nothing you share is sent to a third party; output is local Markdown.

| Capability | What It Does | How |
|------------|-------------|-----|
| **Item classifier** | Detects whether you lost a wallet / phone / passport / keys / laptop / luggage / pet / car / package / jewelry / document | Pattern match + explicit ask |
| **Severity triage** | Classifies lost vs. stolen, at-home vs. abroad, with vs. without cash backup | 4-axis matrix |
| **5-Minute Playbook** | First actions: lock phone, freeze cards, cancel transit cards, disable keys, start Find-My | Per-item runbook |
| **1-Hour Playbook** | File police report, contact issuer, get emergency replacement doc, block SIM | Per-item + per-country |
| **3-Day Playbook** | Replacement docs, insurance claims, fraud disputes, credit bureau alerts | Per-item + jurisdiction |
| **Country-specific hotline / office lookup** | Embassy phone, bank hotline, police non-emergency number, DMV-equivalent | Built-in directory + lookup |
| **Find-My orchestration** | Sequenced instructions: Apple Find My / Google Find My Device / Samsung / Tile / carrier IMEI tracker | Per-device runbook |
| **Fraud dispute scripts** | FCRA / Regulation E / chargeback templates for US banks | Per-bank language |
| **Insurance claim packet** | List of evidence to gather, claim form fields, adjuster talking points | Per-item |
| **Replacement doc checklist** | Required docs + fees + processing time for passport / DL / SSN card / Global Entry | Per-country, per-item |
| **Follow-up scam check** | If someone messages "we found your item, pay shipping" — applies `phishing-link-inspector` | Cross-skill integration |
| **Local log** | Persists incident + actions to `~/.hermes/memories/lost-items.jsonl` for insurance proof | Append-only JSONL |

---

## When to Use

- *"I lost my passport at Heathrow, my flight is in 12 hours"* — emergency travel ID
- *"My wallet was stolen in Barcelona, I have no cash or cards"* — emergency wallet recovery
- *"I can't find my phone — last seen at the office"* — device location + remote wipe
- *"Air Canada lost my suitcase 3 days ago"* — airline baggage claim escalation
- *"Someone used my credit card after I lost my wallet"* — fraud dispute + card replacement
- *"I lost my car keys at the mall, no spare"* — locksmith + key replacement
- *"My dog ran off in the park"* — lost pet playbook (microchip, shelters, social posts)
- *"My laptop was stolen, it had 2FA seeds in it"* — secret rotation + device wipe
- *"I lost my car in a parking garage"* — Find My Car + lot office contact
- *"USPS says delivered but I never got the package"* — porch pirate / mail recovery
- *"My engagement ring slipped off in the ocean"* — lost-and-found + insurance claim
- *手机被偷了，绑定了很多app怎么办* — Chinese-context phone theft
- *护照丢了，明天就要回国* — emergency CN passport replacement
- Any high-stress "I lost X and I don't know what to do first" trigger

---

## Core Workflow

### Step 1: Capture the incident (3 quick questions)

Ask the user, in this exact order:

```text
1. WHAT was lost or stolen?  (wallet / phone / passport / keys / laptop / luggage / pet / car / package / document / jewelry / other)
2. WHERE are you right now?  (home / abroad / in transit / at event)
3. WHEN did you notice it was gone?  (just now / today / yesterday / days ago)
4. (Bonus) Lost or stolen? Suspect?
```

Wait — these 4 questions are the difference between a useful plan and generic advice. Don't skip.

Then classify:

```python
SEVERITY = {
    "stolen":   3,   # worst case — assume credentials compromised
    "lost":     2,   # recoverable but unknown
    "misplaced":1,   # probably still findable
}

CONTEXT = {
    "abroad":     3,  # replacement is hardest
    "in_transit":  2,  # moving — harder to retrace
    "at_home":    1,  # easiest
}

URGENCY = {
    "next_24h_event": 3,  # flight, presentation, court date
    "this_week":      2,
    "no_rush":        1,
}
```

Severity = `max(SEVERITY)` × `max(CONTEXT)` × `max(URGENCY)` → **CRITICAL / HIGH / MEDIUM / LOW**.

---

### Step 2: Generate the 3-tier playbook (5min / 1hr / 3day)

For each lost item, generate three time-bounded action lists. The exact steps depend on `WHAT` — here are the most common runbooks:

#### 🪪 PASSPORT lost/stolen

```text
⏱️ 5 MINUTES
- [ ] Confirm it's actually lost (check bags, hotel safe, front desk, airline seat pocket)
- [ ] If abroad: call your nearest embassy/consulate emergency line NOW
      US abroad: +1-202-501-4444 (after-hours)
      CN abroad: +86-10-12308 (外交部领事保护热线)
- [ ] Photograph the loss (any evidence of where you last had it)
- [ ] Pull a digital copy of your passport photo page from cloud / email

⏱️ 1 HOUR
- [ ] File a police report (REQUIRED for emergency passport issuance abroad)
- [ ] Apply for emergency passport / laissez-passer at embassy/consulate
      Required: police report, photo, fee, application form, ID alternative
- [ ] Notify your airline if traveling within 24h — they may rebook free
- [ ] Notify hotel / accommodation — they sometimes find items

⏱️ 3 DAYS
- [ ] Report lost passport to your home country passport agency (online form)
      US: State Dept DS-64 lost-passport form → https://eforms.state.gov/
      CN: 公安部出入境管理局 report → local PSB exit-entry office
      UK: https://www.gov.uk/report-a-lost-or-stolen-passport
- [ ] Watch for identity-theft signals for 6 months (free credit reports)
- [ ] Update passport number in: renewal-reminder, visa applications, frequent flyer, Global Entry, bank KYC, employer records
- [ ] When new passport arrives → pair with renewal-reminder skill to track 10-year expiry
```

#### 👛 WALLET lost/stolen

```text
⏱️ 5 MINUTES
- [ ] LOCK the device you use for banking apps (Google / Apple ID password)
- [ ] List every card that was in the wallet (photo of wallet contents if you have one)
- [ ] CALL each issuer's "lost/stolen card" line (numbers on back of card, or use app)
      US: 24/7 hotline listed on card issuer site
      Most apps: "Card → Settings → Report lost or stolen"
- [ ] Freeze credit at all 3 bureaus (US) — does NOT affect score
      Equifax: 1-800-685-1111
      Experian: 1-888-397-3742
      TransUnion: 1-888-909-8872
- [ ] File a police report (online form usually available in US)

⏱️ 1 HOUR
- [ ] Review last 24h transactions on every card — note any you didn't make
- [ ] If fraudulent charges: dispute immediately using FCRA / Reg E rights
      US: cardholder liability capped at $50 if reported within 2 business days
- [ ] Replace transit cards (MetroCard, Oyster, Suica, etc.) — many can be transferred
- [ ] If driver's license was in wallet → DMV replacement
- [ ] If health insurance card was in wallet → call insurer for replacement
- [ ] If Social Security card (US) → SSA-3000 form, mail only, 2-4 weeks

⏱️ 3 DAYS
- [ ] If you suspect ID theft: place 1-year fraud alert with one bureau (auto-propagates)
- [ ] File IRS Identity Theft Affidavit (Form 14039) if SSN was in wallet
- [ ] Update auto-pay / subscription cards — subscription-manager skill can find them
- [ ] Consider AAA / roadside assistance card if you had one
- [ ] 6-month credit monitoring — free from each bureau
```

#### 📱 PHONE lost/stolen

```text
⏱️ 5 MINUTES
- [ ] From another device → icloud.com/find (Apple) or android.com/find (Google)
- [ ] Mark as Lost → locks screen + suspends Apple/Google Pay
- [ ] If stolen (not just lost): select Erase (last resort — kills ability to locate)
- [ ] Call your own number from another phone (someone may answer honestly)
- [ ] Retrace your last 2 hours — Uber/Lyft history, recent locations in Maps

⏱️ 1 HOUR
- [ ] Contact carrier → suspend line + blacklist IMEI
      AT&T: 1-800-331-0500   Verizon: 1-800-922-0204   T-Mobile: 1-800-937-8997
      Vodafone: +44 191-282-5000 (UK)
      中国移动: 10086   中国联通: 10010   中国电信: 10000
- [ ] Change passwords for: email, banking, social media, password manager
      Start with the one that has your password manager recovery codes!
- [ ] If phone had 2FA seeds (Google Authenticator, Authy, Yubikey app):
      → log out all sessions, switch to backup codes, rotate secrets
      → use secret-scanner skill to identify which accounts need rotation
- [ ] Notify your employer (if work phone or had work email)
- [ ] If you had crypto wallet app → call wallet provider support IMMEDIATELY

⏱️ 3 DAYS
- [ ] Get replacement SIM / eSIM from carrier store (bring ID)
- [ ] Restore from cloud backup (iCloud / Google Drive)
- [ ] Reinstall authenticator app from backup (if you had backup) or set up new
- [ ] File police report if stolen (needed for carrier blacklist + insurance claim)
- [ ] If phone had credit cards in Apple/Google Wallet → those were suspended, but check statements
- [ ] Add phone to home/renter's insurance claim (if covered)
```

#### 🔑 KEYS (home / car / office)

```text
⏱️ 5 MINUTES
- [ ] Retrace last 4 hours — check all pockets, jacket, gym bag, car
- [ ] Check with front desk / lost-and-found at any location you visited
- [ ] If car keys: spare at home? family member? dealership?

⏱️ 1 HOUR
- [ ] If home keys lost AND address could be inferred from keychain:
      → Change locks today (or schedule with landlord)
      → Cost: $50-300 depending on lock count
- [ ] If car keys (modern fob): call dealership or locksmith
      Replacement fob: $80-400 + programming $50-150
- [ ] If office keys: notify building security NOW — re-key may be needed

⏱️ 3 DAYS
- [ ] Get a spare made once you have replacement (don't be in this situation twice)
- [ ] Consider a Tile/AirTag on keychain going forward
- [ ] Update landlord / property management records if rental
```

#### 💻 LAPTOP lost/stolen

```text
⏱️ 5 MINUTES
- [ ] Find My / Find My Device → Mark as Lost / Lock
- [ ] If stolen: trigger remote wipe (only if no hope of recovery)
- [ ] Change passwords for: email, password manager, banking — assume worst

⏱️ 1 HOUR
- [ ] Revoke all active sessions in password manager / SSO / Google / Apple
- [ ] Rotate API keys / tokens that lived on the machine (use secret-scanner skill
      on the last git commit you made to find them)
- [ ] If 2FA seeds lived on this machine only → see "PHONE lost" 2FA section
- [ ] File police report with serial number (Apple: serial number; PC: bottom sticker)

⏱️ 3 DAYS
- [ ] Notify employer IT if work laptop — they have MDM remote wipe
- [ ] File insurance claim (renter's / homeowner's / dedicated electronics policy)
- [ ] Order replacement → restore from Time Machine / File History / cloud
- [ ] File IRS / FTC identity-theft report if financial / SSN data was on it
```

#### 🧳 LUGGAGE lost by airline

```text
⏱️ 5 MINUTES (at airport, BEFORE leaving baggage claim)
- [ ] Find airline's baggage service office (still in baggage claim area, usually)
- [ ] File Property Irregularity Report (PIR) — get a copy with FILE NUMBER
- [ ] Ask about immediate essentials kit (airline may reimburse toiletries, change of clothes)
- [ ] Get airline's lost-baggage hotline + email

⏱️ 1 HOUR
- [ ] Check airline's tracking portal online with PIR number (refresh every 2-3h)
- [ ] If you have AirTag / Tile in bag → share live location with airline
- [ ] File claim under Montreal Convention if international flight (up to ~$1700 SDR)
- [ ] Document contents: receipts for items in bag, photos of bag before trip

⏱️ 3 DAYS
- [ ] If not found within 21 days → file formal lost baggage claim
- [ ] Submit itemized claim with receipts (most airlines: $1500-3400 limit, varies by carrier)
- [ ] Check homeowner's / travel insurance — they may cover above airline cap
- [ ] If bag had medication / glasses → use medical-visit-companion for replacement script
```

#### 🐕 PET lost

```text
⏱️ 5 MINUTES
- [ ] Stay calm — call pet by name in happy voice, don't chase
- [ ] Check: under decks, in garages, neighbor's yards, favorite hiding spots
- [ ] Bring favorite treat + squeaky toy
- [ ] If found: get microchip scanned at any vet to confirm ownership

⏱️ 1 HOUR
- [ ] Post on Nextdoor, local Lost & Found Pets FB groups, neighborhood apps
- [ ] File lost pet report with: city animal control, local shelters (visit IN PERSON
      daily — phone doesn't always work), microchip registry (AAHA, PetLink)
- [ ] Print 50+ flyers (color, photo, last-se location, your phone, no $ reward)
- [ ] Notify vet — they can flag record if someone brings pet in

⏱️ 3 DAYS
- [ ] Run lost-pet Craigslist /  Craigslist equivalent daily
- [ ] Check shelter websites daily (new intake photos)
- [ ] Leave worn t-shirt / worn item outside your home — scent lure
- [ ] Consider hiring a pet tracker (trained dogs that follow scent) for day 5+
- [ ] Don't give up — pets have been found weeks, even months later
```

#### 📦 PACKAGE marked delivered but missing

```text
⏱️ 5 MINUTES
- [ ] Check with neighbors, front desk, mailroom, parcel locker
- [ ] Check driver's usual drop spot (behind planter, side door, etc.)

⏱️ 1 HOUR
- [ ] Check tracking again — sometimes "delivered" is a scan, not actual drop
      Wait 24h before reporting — packages often arrive next morning
- [ ] File "lost package" claim with carrier
      USPS: 1-800-275-8777 (file after 24h)
      UPS: 1-800-742-5877
      FedEx: 1-800-463-3339
      DHL: 1-800-225-5345
- [ ] Contact sender / retailer for replacement or refund

⏱️ 3 DAYS
- [ ] File police report if high-value (porch pirate)
- [ ] File USPS Mail Theft complaint if USPS (uspis.gov)
- [ ] If credit card was used → dispute through your bank
```

#### 🚗 CAR lost/stolen

```text
⏱️ 5 MINUTES
- [ ] Retrace: did you really park where you think? Check parking app history
- [ ] "Find My Car" — iPhone Maps → select destination → "Directions" → parked location
- [ ] Walk the garage level by level, taking photos of license plates

⏱️ 1 HOUR
- [ ] If not found: file stolen vehicle report with police (need VIN, plate, make/model)
- [ ] Notify insurance → opens stolen vehicle case, may cover rental
- [ ] Notify lender if financed (they require this)
- [ ] If you have an AirTag / aftermarket GPS tracker → share location with police
- [ ] If you parked it for someone else (valet, mechanic) → contact them FIRST

⏱️ 3 DAYS
- [ ] Tow lots — call all local ones, daily
- [ ] Plate reader alerts — some police dept auto-alert on patrol
- [ ] Update car-maintenance-tracker with incident for insurance record
```

---

### Step 3: Country-specific hotlines & replacement offices

After the playbook, append a country-aware reference card. Built-in lookup:

```text
🇺🇸 US
  Police non-emergency: 311
  FBI IC3 (cybercrime): https://www.ic3.gov
  FTC Identity Theft: https://www.identitytheft.gov  /  1-877-438-4338
  IRS ID Theft: 1-800-908-4490
  USPS Mail Theft: https://www.uspis.gov/report
  State Dept (lost passport abroad): +1-202-501-4444
  Roadside / DMV: varies by state

🇬🇧 UK
  Police non-emergency: 101
  Action Fraud: 0300-123-2040
  Lost passport: https://www.gov.uk/report-a-lost-or-stolen-passport
  DVLA (lost DL): https://www.gov.uk/replace-driving-licence

🇨🇳 CN
  110 (police) / 12345 (gov hotline)
  外交部领事保护: +86-10-12308
  出入境证件: local 公安局 出入境管理大队
  银行卡挂失: 各行客服 (工行95588 / 招行95555 / 中行95566 / 建行95533)
  手机报停: 10086 / 10010 / 10000

🇪🇺 EU
  112 (emergency) / national police non-emergency
  European Emergency ID: 112 app stores passport data for emergency services
  Schengen consular protection: home country embassy/consulate

🇯🇵 JP
  110 (police) / 119 (ambulance)
  都県警本部 遺失物センター: 03-3814-4151 (Tokyo)
  パスポート再発行: 都道府県旅券事務所
```

---

### Step 4: Generate the dispute / claim packet

If the loss involved financial fraud or insurance claim, generate:

```text
📋 FRAUD DISPUTE PACKET
─────────────────────────
1. Written dispute letter (template below)
2. List of fraudulent charges (date, amount, merchant)
3. Copy of police report
4. Card statements showing the charges
5. Your bank's dispute form (most have an online version)

Template letter (US):
"To whom it may concern,
 I am writing to dispute the following unauthorized charges on my
 [card name] ending in [XXXX], which was [lost/stolen] on [date].
 Per the Fair Credit Billing Act, I am providing this notice
 within 60 days of the statement containing the first unauthorized charge.
 Please investigate and reverse the following transactions:
 [list]
 I have filed a police report (copy attached, case #XXXXX).
 Sincerely, [name]"

📋 INSURANCE CLAIM PACKET
──────────────────────────
1. Police report (REQUIRED for theft)
2. Photos / receipts of the item
3. Purchase proof (credit card statement, original receipt)
4. Replacement quote (current market value)
5. Completed claim form (carrier-specific or homeowner's Form A)
6. Timeline of events (date lost, date discovered, date reported)
```

---

### Step 5: Persist + follow-up

Append to `~/.hermes/memories/lost-items.jsonl`:

```jsonl
{"date":"2026-09-07T14:23:00","item":"wallet","severity":"CRITICAL","context":"abroad","location":"Barcelona","police_report":"BCN-2026-0907-4321","cards_frozen":4,"follow_ups":["replacement_DL","replacement_passport","fraud_dispute","credit_monitoring"]}
```

This powers:
- Reminders in 7 days: *"Did your replacement documents arrive?"*
- Reminders in 30 days: *"Check credit report for new accounts opened in your name"*
- Reminders in 90 days: *"If item recovered, undo Find-My wipe; if not, finalize insurance claim"*
- Cross-skill trigger: if passport lost → `renewal-reminder` gets the new passport number & 10-year expiry

---

## Example Invocations

### Example 1: Passport lost before flight

> **User:** I'm at Heathrow, my flight home is in 11 hours, and I just realized my passport is gone. I went through security 90 minutes ago and I don't see it anywhere.
>
> **Hermes:**
> ```
> 🚨 CRITICAL — Lost passport, abroad, 11h before flight
>
> ⏱️ NEXT 5 MINUTES
> 1. Don't leave the terminal. Walk back to security / passport control lost-and-found.
> 2. Call US Embassy London: +44 20-7499-9000 (24h line: +1-202-501-4444).
> 3. Pull your digital passport photo from email / cloud / phone of phone.
>
> ⏱️ NEXT 1 HOUR
> 4. Get to the US Embassy in person (24 Grosvenor Square) — emergency passport / laissez-passer can be issued same-day.
>    Required: police report (file at Heathrow police station first, in Terminal 2 or 5),
>    photo, DS-11 form, $110 fee, photo ID alternative (driver's license + photocopy).
> 5. File British police report — required for emergency US passport issuance.
> 6. Call your airline (BA / AA / etc.) — they may rebook or provide a letter for embassy.
>
> ⏱️ NEXT 24 HOURS
> 7. Submit DS-64 (lost passport report) online after emergency passport issued.
> 8. Once home, monitor credit reports (Equifax / Experian / TransUnion) for 6 months.
> 9. Update renewal-reminder with new passport number + 10-year expiry.
>
> 🇺🇸 HOTLINES
>  - US Embassy London: +44 20-7499-9000
>  - State Dept 24h: +1-202-501-4444
>  - Heathrow Police: 020-8897-5979
> ```
>
> I'll log this incident to ~/.hermes/memories/lost-items.jsonl and remind you in 30 days to check your credit report. Want me to also queue a follow-up with renewal-reminder for the new passport?

### Example 2: Wallet stolen in Barcelona

> **User:** My wallet got stolen in Barcelona, I have no cash or cards. I'm at the hotel. I have my phone.
>
> **Hermes:**
> ```
> 🚨 CRITICAL — Stolen wallet, abroad, all cards compromised
>
> ⏱️ NEXT 5 MINUTES (sit down, do these one by one)
> 1. LOCK your iPhone / Google account NOW (someone with your ID + phone might try).
> 2. List the cards in your wallet:
>    - Chase Sapphire, ending 4521 (call: 1-800-432-3117)
>    - Amex Platinum, ending 1003 (call: 1-800-992-3404)
>    - Bank of America debit, ending 7782 (call: 1-800-432-1000)
>    - Driver's license (CA)
> 3. CALL each number above → "Report lost or stolen card". Do this in parallel with help.
> 4. File a Spanish police report online: https://sede.policia.gob.es
>    (or at nearest comisaría). Save the case number — you need it for everything.
>
> ⏱️ NEXT 1 HOUR
> 5. Review last 24h transactions on Chase / Amex apps (use your phone).
>    Any charges you didn't make? → Dispute immediately using FCRA rights.
> 6. Freeze credit at the 3 US bureaus (costs $0, doesn't hurt score):
>    - Equifax 1-800-685-1111  •  Experian 1-888-397-3742  •  TransUnion 1-888-909-8872
> 7. Get emergency cash via Western Union (hotel can direct you) using passport as ID.
>
> ⏱️ NEXT 3 DAYS
> 8. If driver's license was in wallet → order replacement from CA DMV online (Form DL 44).
> 9. If charges were made → file written dispute letter to each issuer (template I'll send).
> 10. Place 1-year fraud alert with one bureau (it propagates to all 3).
>
> I have a fraud dispute letter template ready for your Chase + Amex cards.
> Want me to draft them with the charge details from your statements?
> ```
>
> I'll log this incident. In 7 days I'll ask if replacement documents arrived; in 30 days I'll remind you to pull free credit reports.

### Example 3: Phone lost in cab

> **User:** I left my phone in a Lyft. It's been 30 min. I have my laptop but no other device.
>
> **Hermes:**
> ```
> ⏱️ NEXT 5 MINUTES (open laptop browser)
> 1. Go to icloud.com/find → sign in with your Apple ID → Find iPhone.
>    Click your phone → "Mark as Lost" (locks screen, suspends Apple Pay).
>    DO NOT click Erase yet — keep ability to locate.
> 2. Call your own number from laptop (FaceTime / Google Voice / any VoIP).
> 3. Open Lyft app on laptop → ride history → "Contact driver" about lost item.
>
> ⏱️ NEXT 1 HOUR
> 4. If Lyft driver doesn't respond in 30 min → Lyft lost & found: help.lyft.com
>    They'll coordinate with the driver — usually items returned within 24h.
> 5. If you have an AirTag on the phone case → check its location live in Find My.
> 6. If you DO find it → cancel "Mark as Lost".
> 7. If you DON'T find it after 24h → click Erase from icloud.com/find.
> 8. Once you erase → contact carrier for replacement SIM (AT&T / Verizon / T-Mobile store).
>
> ⏱️ NEXT 3 DAYS
> 9. Restore new phone from iCloud backup.
> 10. Re-authenticate 2FA seeds — anything that lived only on this phone needs reset
>     (Authy / Google Authenticator without cloud backup is the risk).
> 11. If phone had credit cards in Apple Wallet → confirm charges, those cards were auto-suspended.
>
> Want me to draft a message to the Lyft driver for you?
> ```
>
> ```text
> "Hi! I left my iPhone in your car on the ride from [pickup] to [dropoff] at [time].
>  It's a [color] iPhone [model] in a [case]. If you found it, I can meet you
>  nearby or cover the cost of dropping it off. Thanks so much — really appreciate it!"
> ```

---

## Common Pitfalls

| Pitfall | Why it hurts | Fix |
|---------|-------------|-----|
| **Calling your bank before you file a police report** | Banks often won't process fraud claims without a police report number | File police report FIRST (online form takes 5 min), then call |
| **Erasing the iPhone immediately when stolen** | You lose the ability to track, see live location, or get it back via police | Mark as Lost first; only Erase after 24-48h with no recovery |
| **Not freezing credit at all 3 bureaus** | One bureau freeze is incomplete; new accounts can still be opened at the others | Freeze at all 3 (US: $0 each, instant online) |
| **Posting "Lost X, reward $$$" publicly** | Scammers target these posts pretending to have your item | Use generic photo, contact-only, no reward amount; cross-check any "finder" message with `phishing-link-inspector` |
| **Waiting too long to file police report** | Many replacements (passport, ID) require police report filed within 24-48h | File online if station is closed; police report = evidence anchor |
| **Assuming you're not at risk of identity theft** | Lost wallet = SSN + DOB + cards. New accounts can be opened in your name for years | Freeze credit + fraud alert + 6-month monitoring minimum |
| **Using "lost/stolen" on airline PIR when bag was delayed** | PIR type determines claim path; wrong type = denied | Get the PIR type from airline agent, write it down |
| **Following a "we found your item" text link** | Classic phishing after-the-fact scam | Treat any follow-up message asking for $$ / info as suspect — use `phishing-link-inspector` |
| **Not keeping photo of wallet contents** | You can't remember all 12 cards 3 days later; banks ask for card list | Take phone photo of wallet contents today; store in cloud |
| **Skipping the "5-min" items because they feel small** | The 5-min list is the highest-leverage — locks + freezes take minutes but block most downstream damage | Do the 5-min list first, always, even if it feels redundant |
| **Going to embassy without required docs** | Emergency passport issuance denied; you wait days | Call embassy FIRST to confirm exact document list before going |
| **Reporting "stolen" when item is actually "lost"** | Changes insurance claim category, police follow-up priority, and FBI report filing | Be honest with insurer about "lost vs. stolen" — it affects payout |

---

## Verification Checklist

Before delivering the playbook, verify:

- [ ] Confirmed WHAT was lost (item type unambiguous)
- [ ] Confirmed WHERE user is right now (country / city)
- [ ] Confirmed WHEN user noticed it gone (within last hour / today / yesterday)
- [ ] Classified severity as CRITICAL / HIGH / MEDIUM / LOW using the 3-axis matrix
- [ ] Generated all 3 time-bounded action lists (5min / 1hr / 3day)
- [ ] Country-appropriate hotline / phone numbers included
- [ ] Police report step listed (if stolen / passport / high-value)
- [ ] Card-freeze steps listed (if wallet / cards involved)
- [ ] Find-My device step listed (if phone / laptop involved)
- [ ] Fraud dispute packet offered (if any financial instrument involved)
- [ ] Insurance claim packet offered (if high-value item)
- [ ] Cross-skill triggers fired (`renewal-reminder` for IDs, `subscription-manager` for cards, `phishing-link-inspector` for follow-ups)
- [ ] Incident logged to `~/.hermes/memories/lost-items.jsonl`
- [ ] 7-day / 30-day / 90-day follow-up reminders queued
- [ ] Output is calm, time-ordered, and actionable — not a wall of generic advice

---

## Data Sources & Accuracy

| Source | Used For |
|--------|---------|
| **US State Dept** | Lost passport DS-64 form, emergency passport requirements |
| **US FTC IdentityTheft.gov** | Identity theft recovery steps, fraud alert, credit freeze procedure |
| **US FCRA / Reg E** | Cardholder liability limits, dispute timelines, written notice template |
| **Apple Find My / Google Find My Device** | Lock / wipe / locate device workflows |
| **Major US carrier hotlines** (AT&T/Verizon/T-Mobile) | SIM suspension, IMEI blacklist, replacement SIM |
| **US 3 credit bureaus** (Equifax / Experian / TransUnion) | Credit freeze + fraud alert phone numbers + URLs |
| **UK gov.uk** | Lost passport form, Action Fraud, DVLA replacement |
| **中国外交部 / 公安部** | +86-10-12308 领事保护热线, 出入境证件补办 |
| **Schengen / EU 112** | European emergency services, consular protection |
| **Montreal Convention 1999** | International airline lost baggage liability limits (≈1700 SDR) |
| **IATA / airline PIR standards** | Baggage claim filing, escalation paths |
| **Each bank's published lost-card procedure** | Per-bank dispute letter templates + phone scripts |

> ⚠️ **Important**: Hotline numbers, URLs, and procedures change. The skill verifies the current number against the official source whenever possible, but always tells the user to confirm by visiting the official website (linked, not "click here"). For financial losses >$500, the skill recommends contacting a licensed attorney or your home country's consumer protection agency before accepting an insurer's first settlement.

> 🔒 **Privacy**: This skill processes only the incident details the user shares. The optional `~/.hermes/memories/lost-items.jsonl` log stays on-device and is for the user's own follow-up reminders. Nothing is sent to a third party without explicit user action.

> 🤝 **Pairs well with**: `renewal-reminder` (track new ID expiry), `travel-itinerary-planner` (trip context, embassy hours), `personal-crm` (who to contact at hotels/airlines), `phishing-link-inspector` (vet follow-up "finder" messages), `secret-scanner` (if laptop had API keys), `subscription-manager` (find recurring charges on stolen card), `car-maintenance-tracker` (incident log for stolen vehicle insurance claim).