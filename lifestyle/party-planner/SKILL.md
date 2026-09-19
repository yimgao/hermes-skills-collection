---
name: party-planner
description: "Plan any gathering end-to-end from chat — birthday, dinner party, holiday, baby shower, housewarming, retirement. Generates theme, guest list, invitations, budget, menu, shopping list, run-of-show timeline, day-of checklist, and post-party teardown. Adapts to size (intimate 4 to 80+) and venue (home / park / venue / virtual)."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [party, event-planning, hosting, dinner-party, birthday, celebration, gathering, lifestyle, hospitality]
    related_skills: [gift-finder, recipe-generator, weekly-meal-planner, personal-crm, pantry-manager, travel-itinerary-planner]
---

# Party Planner / 聚会策划

> Plan a complete party from a single chat prompt. Handles theme, guest list, invitations, budget, menu, shopping list, run-of-show, day-of checklist, and teardown — for any occasion, any size, any venue.

---

## Overview

This skill turns "I'm throwing a party on Saturday" into a complete, executable plan. It generates every artifact a host needs: invitation text, menu, shopping list, cooking timeline, run-of-show minute-by-minute, day-of checklist, and post-party wrap-up. It scales from an intimate 4-person dinner to an 80-person milestone birthday, and adapts to whatever constraints the host gives (budget, venue, dietary needs, time).

The goal: the host should never have to ask "wait, what time do I take the turkey out?" or "did I forget the ice?" — every decision is pre-made in the plan.

| Capability | What it produces |
|---|---|
| **Theme & concept** | Vibe / palette / dress code / signature element |
| **Guest list** | RSVP tracker, seating chart (for sit-down dinners) |
| **Invitations** | Channel-appropriate copy (text / email / Evite / paper) |
| **Budget** | Itemized estimate (food / drink / decor / entertainment / paper goods / misc) |
| **Menu** | Cook-from-scratch OR order-ahead OR potluck, with dietary coverage |
| **Shopping list** | Consolidated, deduplicated, aisle-grouped, quantity-aware |
| **Cooking timeline** | T-minus countdown (D-7 → D-day) — what to prep when |
| **Run-of-show** | Minute-by-minute schedule for the day of, with owners |
| **Day-of checklist** | Pre-guest, mid-event, post-event checklists |
| **Post-party** | Thank-you messages, leftover plan, venue reset |

---

## When to Use

- User asks: *"I'm throwing my mom a 60th birthday dinner for 12 — help me plan it"*
- User asks: *"Plan a casual backyard BBQ for 25 next Saturday, $300 budget"*
- User asks: *"帮我策划一个 8 人的感恩节晚宴"*
- User asks: *"I'm hosting a baby shower — 20 guests, vegan + 1 gluten-free"*
- User asks: *"Office holiday party for 40, catered, in our conference room"*
- User asks: *"Last-minute NYE party for 10, what can I pull together tonight?"*
- User asks: *"Housewarming, 30 people, mostly couples, in my new apartment"*
- User asks: *"Virtual game night for 8 friends across 3 time zones"*

---

## Core Workflow

### Step 1: Intake — Lock the 6 Critical Variables

Ask (or infer from prompt) the minimum needed to design the party. If the user gives nothing, propose defaults and confirm.

| Variable | Required | Description | Default |
|---|---|---|---|
| `occasion` | ✅ Yes | What's it for? | — |
| `date` | ✅ Yes | When | — |
| `guest_count` | ✅ Yes | How many | 8 |
| `venue` | ❌ No | Home / friend's home / park / restaurant private room / venue / virtual | Host's home |
| `budget_total` | ❌ No | Total $ (USD/CNY/EUR) | $25/person |
| `vibe` | ❌ No | Casual / semi-formal / formal / themed / surprise | Casual |
| `dietary` | ❌ No | Vegetarian count, vegan, gluten-free, allergies, halal/kosher | Mixed |
| `style` | ❌ No | Cook at home / order-ahead / potluck / fully catered | Cook at home |
| `time_window` | ❌ No | Start–end (e.g., 6pm–10pm) | 3 hours |
| `must_haves` | ❌ No | Cake? Music? Photo backdrop? Games? Speeches? | None |
| `no_gos` | ❌ No | What to avoid (e.g., no alcohol, no flowers) | None |

If `guest_count` < 4 → warn that "intimate" framing changes plan (sit-down, single conversation, no amplification).
If `guest_count` > 30 → trigger "large event" path (catering or potluck strongly recommended, no sit-down, need helpers).

### Step 2: Generate Theme & Concept

Pick a theme that matches occasion + vibe. Output:

- **Theme name** (1 line)
- **Color palette** (3 colors + 1 accent)
- **Dress code** (or "come as you are")
- **Signature element** (the one memorable thing — signature cocktail, photo wall, ice sculpture, themed playlist, custom menu cards)
- **Music direction** (genre / vibe / playlist search terms)

For surprise parties: add a cover-story plan so guests who stumble in early don't blow it.

### Step 3: Build Guest List & Invitations

**Guest list helper:**
- If user has names, use them
- Else, prompt for: how many couples / singles / kids / VIPs / must-invite-else-drama
- Calculate table/seating needs: 8-person rounds, 6-person rectangles, high-tops, etc.

**Invitation copy (channel-aware):**

| Channel | Format | Length |
|---|---|---|
| **Text / WhatsApp / iMessage** | 2-3 sentences, emoji-light, RSVP bit.ly or "reply YES/NO by [date]" | < 300 chars |
| **Email** | Subject + 3-paragraph body + RSVP button text + calendar invite attached | 200 words |
| **Evite / Paperless Post** | Title + cover image suggestion + body + RSVP link | Standard |
| **Paper invitation (formal)** | Wording for printed card + envelope addressing | Formal |

Generate at least one channel by default; ask if user wants others.

### Step 4: Budget & Menu

**Budget split by event size:**

| Category | Intimate (≤8) | Medium (9-25) | Large (26+) |
|---|---|---|---|
| Food | 50% | 45% | 35% (catered) |
| Drink | 20% | 20% | 20% |
| Decor | 10% | 15% | 15% |
| Entertainment | 5% | 10% | 15% |
| Paper goods / serveware | 5% | 5% | 10% |
| Misc (tips, contingency) | 10% | 5% | 5% |

**Menu design rules:**
- For sit-down dinners: 1 appetizer + 1 main + 1 side + 1 dessert + drink pairing (cook: 60% of effort, order: 40%)
- For buffets: 2 mains + 3 sides + 2 salads + 1 dessert + drink station
- For potlucks: host provides anchor (main or drinks), guests fill gaps; coordinate to avoid 4 potato salads
- For cocktail parties: 6-8 finger foods per 25 guests + 2-3 batch cocktails
- Always: 1 vegetarian default, 1 gluten-free default, label everything
- For 8+ guests with food allergies: build a tagged allergen matrix

**Cooking load warning:**
- > 6 dishes for > 12 guests cooked day-of = high failure risk. Recommend at least 1 cold prep + 1 order-ahead.

### Step 5: Shopping List (Quantities Aware)

Generate a deduplicated, aisle-grouped shopping list:

```
PRODUCE:
- 3 lbs baby carrots (2 lbs glazed + 1 lb crudité)
- 2 lbs mixed greens
- 1 bunch fresh thyme
- 4 lemons
- 1 pint raspberries

DAIRY:
- 1.5 lbs salted butter (3 sticks for glaze, 1 stick for mash, extra)
- 1 quart heavy cream
- 8 oz block parmesan
- 1 dozen eggs

PROTEIN:
- 5 lbs whole chicken (for 12 ppl, 8 oz cooked protein each)
- 2 lbs salmon fillet

PANTRY:
- Olive oil, kosher salt, black pepper, garlic (4 heads)
...

DRINKS:
- 6 bottles Sauvignon blanc (rule: 1 bottle per 3 guests for 3-hr wine event)
- 24 bottles sparkling water
- 12-pack lager
- 1 bag ice (10 lb) — and a backup 10 lb bag

PAPER GOODS:
- 30 napkins (cloth > paper if small event)
- 25 plates (9" dinner)
- 25 bowls
- 25 sets cutlery
- 30 cups (mix glass + disposable)

DECOR:
- 3 bouquets peonies (Trader Joe's / Costco / wholesale)
- 50 tea lights + matches
- 1 string café lights (outdoor)
```

**Quantity formulas** (use these so user doesn't have to think):

| Item | Formula |
|---|---|
| Main protein | `guests × 6-8 oz raw weight per person` |
| Side starch | `guests × 4-6 oz cooked` |
| Salad | `1.5 oz greens per person` |
| Wine | `1 bottle per 3 guests` (for 3-hr event) |
| Beer | `2 per guest for first hour + 1/hour after` |
| Spirits | `1 bottle (750ml) per 6-8 guests` |
| Sparkling water | `1 per guest + 50% buffer` |
| Ice | `1.5 lbs per guest (outdoor); 0.5 lbs (indoor)` |
| Napkins | `2.5× guest count` |
| Plates (buffet) | `1.5× guest count` (appetizer + dinner) |
| Coffee | `1 cup per 2 guests (post-meal)` |

### Step 6: Cooking & Prep Timeline (D-countdown)

Generate a reverse timeline from event start. Always include buffer.

**Example for a 6pm dinner, 10 guests, sit-down:**

```
D-7 to D-3 (PICKUP WEEK):
  □ D-7: Send invitations; confirm RSVPs
  □ D-7: Reserve rentals / confirm venue
  □ D-5: Order cake / special ingredients
  □ D-3: Confirm headcount; finalize menu based on dietary
  □ D-3: Print menu cards + place cards + seating chart

D-2 (PREP DAY):
  □ AM: Grocery run (per shopping list)
  □ AM: Make dessert (most things improve overnight)
  □ PM: Brine / marinate protein
  □ PM: Make salad dressing, chop aromatics (onions, garlic, herbs)
  □ PM: Set table; arrange furniture for flow
  □ PM: Test playlist / lighting

D-1 (DAY BEFORE):
  □ AM: Bake / make anything that holds (rolls, pie crust, sauces)
  □ PM: Chop vegetables for sides; portion into containers
  □ PM: Set up bar / drink station
  □ PM: Chill all glassware, serving platters, ice buckets
  □ PM: Confirm any helpers / hired hands (bartender, server)
  □ PM: Lay out your outfit
  □ PM: Charge camera / phones / speakers

D-DAY (EVENT DAY):
  □ 9 AM:  Take meat out to come to room temp (if applicable)
  □ 10 AM: Make cold apps; finish any cold prep
  □ 12 PM: LIGHT meal for yourself (skip the "host doesn't eat" trap)
  □ 1 PM:  Set out serving platters, utensils, napkins per station
  □ 2 PM:  Decor — flowers, candles, lights, music test
  □ 3 PM:  Start mains that need long cook (roast, braise)
  □ 4 PM:  Quick shower / change / rest 20 min
  □ 4:30 PM: Open wine to breathe; pour welcome cocktail batch
  □ 5 PM:  Final oven check; verify all platters have serving tools
  □ 5:30 PM: Trash bag staged; guest towels placed
  □ 5:45 PM: Door unlocks; music on; YOU breathe

D+1 (DAY AFTER):
  □ AM: Send thank-you texts (within 24 hrs = gold standard)
  □ AM: Package leftovers; label; deliver / invite friends to grab
  □ PM: Return rentals
  □ PM: Write down what worked / what didn't (in party-planner journal)
```

Adapt based on event type (BBQ = different cadence; cocktail party = mostly D-1 / D-day; catered = mostly coordination).

### Step 7: Run-of-Show (Minute-by-Minute)

For the event day, write a clock-time schedule with **owners**. Critical for any event with > 6 guests or any setup/teardown that needs multiple hands.

**Template:**
```
5:00 PM  [Host]  Welcome drink poured; music on; door opens
5:05 PM  [Helper] Coat / bag station set; candles lit
5:15 PM  [Host]  Greet arrivals; offer drink
5:45 PM  [Host]  "Food in 10" announcement
5:55 PM  [Helper] Move apps off table; main course service
6:00 PM  [All]   Sit / buffet opens
6:45 PM  [Host]  Dessert + coffee service
7:00 PM  [Helper] Clear plates; restock drinks
7:15 PM  [Host]  Toast / cake / speeches (if applicable)
7:45 PM  [Helper] Open games / music louder / wind-down mode
9:30 PM  [Host]  "Last call" cue
9:45 PM  [Helper] Begin tidying bar
10:00 PM [All]   Wrap; thank guests; see out
10:30 PM [Host]  Quick reset for morning (do NOT do full clean tonight)
```

For < 8 guests: skip the minute-by-minute, just provide a flow cue sheet (welcome → apps → main → dessert → wind-down).

### Step 8: Day-of Checklists (3 of Them)

**Pre-guest checklist** (run-through 30 min before):
```
□ Bathroom: clean, fresh hand towel, soap, plunger visible
□ Entryway: clear path; coat pile area set
□ Lighting: warm / on dimmer; candles lit; outdoor lights on if dusk
□ Music: queued, volume level appropriate for first 30 min
□ Bar: ice full; glasses out; one bottle each of red/white open
□ Apps: arranged on serving board; napkins next to it
□ Seating: arranged for flow; extra chairs accessible
□ Trash: bag in can; extra bag at bar; recycling bin visible
□ Phone: silent / do-not-disturb on (except ringer for emergencies)
□ Camera: ready; backup battery
□ Pets: secured / fed / put away
□ Kid zone: set (if any kids attending)
□ Personal: breath mint, stain-stick, host outfit clean
```

**Mid-event pulse (90 min in):**
```
□ Ice still full? Refill.
□ Drinks still stocked? Replenish.
□ Trash over 60%? Empty.
□ Anyone standing alone? Pull them into conversation.
□ Anyone too drunk? Get them water + ride.
□ Bathroom check (refresh towels).
□ Music: shift playlist if energy dipping.
```

**Post-event teardown:**
```
□ Thank every guest at the door
□ All guests have ride / safe transport
□ Leftovers: package + label; dish ownership clear
□ Kitchen soak: fill sink with soapy water for dishes (don't scrub tonight)
□ Trash: full bag out; recycling sorted
□ Bathroom quick wipe; fresh towel for morning
□ Lost & found: one bin for forgotten items
□ Anything borrowed returned? (chargers, candles, serving boards)
□ Door locked / windows closed / oven off / stove off
□ YOU: debrief in 1 line, sleep
```

### Step 9: Save & Hand Off

Save the complete plan:

```
~/events/{YYYY-MM-DD}-{slug}/plan.md          # the master plan
~/events/{YYYY-MM-DD}-{slug}/shopping.md      # shopping list (paste into Notes/Wunderlist/Reminders)
~/events/{YYYY-MM-DD}-{slug}/timeline.md      # cooking timeline + run-of-show
~/events/{YYYY-MM-DD}-{slug}/post-mortem.md   # filled in D+1
```

For virtual events: also generate calendar invites (.ics) and a Zoom/Meet link reminder.

---

## Example Invocations

### Example 1: Milestone Birthday Dinner
```
User: My mom's turning 60, I want a sit-down dinner at home for 12 people,
      Saturday Nov 15 at 7pm. Budget $600 total. Mom is vegetarian,
      one guest is gluten-free, one has nut allergy. Vibe: warm,
      elegant but not stuffy. Surprise — only immediate family knows.

Hermes should:
  1. Generate theme: "Golden Hour" — warm amber + cream + gold accents
  2. Suggest 3-course vegetarian-forward menu with gluten-free + nut-free annotations
  3. Build budget: $600 → $360 food, $120 wine, $60 flowers/decor, $40 cake, $20 misc
  4. Write invitation copy for text/email — save-the-date separate from full invite
  5. Generate shopping list with quantity formulas
  6. Cooking timeline D-7 → D-day
  7. Run-of-show 6pm setup → 11pm wrap
  8. Day-of checklists (pre/mid/post)
  9. Save plan to ~/events/2025-11-15-moms-60th/
  10. Flag: "Confirm no one in the 12 has celiac vs preference, since menu differs"
```

### Example 2: Casual Backyard BBQ
```
User: Backyard BBQ, July 4th, 25 people, super casual, $300 budget,
      4pm-9pm. Mixed group — 3 kids, 5 vegetarians, 1 vegan.
      I have a grill but no help. I want it easy.

Hermes should:
  1. Suggest: potluck-style with host doing grill + 1 side + drinks
  2. Generate menu: 2 mains (chicken + portobello for veg), 3 sides easy/cook-ahead,
     1 dessert (no-bake), 2 batch cocktails + beer/wine/soda
  3. Quantity-formula the shopping list; flag hot dogs are easier than burger grinding
  4. Suggest assignment for potluck (use sign-up sheet or just ask 4 friends to each
     bring a side)
  5. Run-of-show: 2pm setup, 4pm door, 6pm eat, 7pm fireworks
  6. Day-of checklist trimmed for outdoor (extra: sunscreen, citronella, shade plan)
  7. Note: "For 25 with 1 host, set hard cutoff at 9pm or you'll be cleaning until midnight"
```

### Example 3: Last-Minute NYE Cocktail Party
```
User: I just decided I'm hosting a NYE party tonight, 10 people,
      my apartment, 9pm-1am. I can cook OR order, budget $200,
      no particular theme. Give me a complete plan in 30 min.

Hermes should:
  1. Recommend ORDER + 2 homemade things (one cocktail batch + one showstopper dip)
  2. Suggest pickup: rotisserie chicken + sides from Whole Foods; bakery dessert;
     supplement with 1 charcuterie board from fridge
  3. Cocktail: 1 batch something (Negroni / whiskey sour / paloma — pick by what's in
     their likely bar — ask what they have)
  4. Time plan (TODAY): 6pm shop, 7pm clean, 8pm setup, 8:30pm shower, 9pm door
  5. Shopping list optimized for ONE trip with everything within walking distance
  6. Note: "Don't try to be a hero at midnight — have snacks pre-portioned and a
     countdown app ready"
  7. Mini run-of-show just for the night (welcome → apps → midnight toast → wind-down)
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---|---|
| 1 | **Host doesn't eat.** You spent 5 hours cooking and forgot your own plate. | Calendar block: "HOST MEAL — 12pm, full sit-down lunch." Hard rule. |
| 2 | **Cooking too much, day-of.** Six raw dishes for 12 people = chaos. | Cold-prep at least 2 items day-before; order 1 hero item; embrace the "low cook" party. |
| 3 | **Not enough ice.** #1 mistake for outdoor/drink-heavy events. | Buy 1.5× the formula amount; backup bag in freezer; ice bucket rotated. |
| 4 | **Dietary blind spots.** Surprise: 3 guests are vegetarian, not "1 maybe." | Explicit RSVP question: "Any allergies / diet I should know?" — require reply. |
| 5 | **Music at wrong volume.** Too loud = shouting; too soft = awkward silence. | Test with door closed; mid-volume early, raise as alcohol flows; have 3 playlists (arrival / dinner / dance). |
| 6 | **No flow / no structure.** Guests cluster; conversations die; awkward pockets. | For 8+ guests: anchor every 90 min — apps, sit, dessert, activity, last call. |
| 7 | **No helpers = burnout.** 25-person event solo = guaranteed bad time. | Recruit at least 1 helper per 10 guests; assign owner to each checklist block. |
| 8 | **Setup too late.** You're mopping when doorbell rings. | Lock setup end-time 30 min before door; have a "do not start anything new" cutoff. |
| 9 | **Forgetting the bathroom.** #1 unspoken guest complaint. | Mid-event pulse must include bathroom check (towel, soap, plunger visibility). |
| 10 | **Leftovers go bad.** $200 of food wasted in fridge. | D+1 morning: portion into labeled containers; text "come grab" or drop at friend's door. |
| 11 | **No thank-yous.** People remember the absence. | Send within 24 hrs; text/voice note > email for casual; card for formal. |
| 12 | **No de-brief.** You do it again, same mistakes. | D+1 evening: 5-line post-mortem: what worked / what to change / vendor notes / thank-yous to send. |

---

## Verification Checklist

Before saving the final plan, confirm:

- [ ] All 6 critical variables captured (occasion, date, count, venue, budget, vibe)
- [ ] Theme + color palette + signature element defined
- [ ] Invitation copy written for at least 1 channel
- [ ] RSVP deadline set (typically D-7 to D-10 for sit-down, D-3 for casual)
- [ ] Menu covers all dietary constraints with explicit dishes
- [ ] Budget split sums to 100% with concrete $
- [ ] Shopping list is aisle-grouped + deduplicated + quantity-formula-derived
- [ ] Cooking timeline has clear D-countdown blocks
- [ ] Run-of-show has clock times AND owners (for 8+ guests)
- [ ] All 3 day-of checklists present (pre / mid / post)
- [ ] Helper count: at least 1 per 10 guests for medium+ events
- [ ] Leftover plan + thank-you reminder included
- [ ] Saved to ~/events/{date}-{slug}/ with all 4 files
- [ ] If surprise: cover story documented; accomplice roles assigned
- [ ] If virtual: tech stack (Zoom/Meet) + etiquette tested D-1

---

## Data Sources & Accuracy

This skill is mostly generative (the plan is original to the user's brief) but draws on a few inputs that should be verified:

| Input | Source | When to verify |
|---|---|---|
| Venue capacity / rules | Venue contract or host's measurement | Before finalizing guest count |
| Local vendor hours (bakery, florist, rental) | Google Maps / vendor site | D-3 or earlier if custom items |
| Weather forecast | weather.com / Apple Weather | D-3 and D-1 for outdoor events |
| Alcohol delivery minimums | Drizly / Instacart / local liquor store | D-2 |
| Dietary needs | Direct RSVP ask | Before menu is locked |
| Rental availability | Party rental company | D-7 minimum for popular weekends |
| Calendar conflicts (for the host's helpers) | Ask directly | D-3 |

### What NOT to rely on
- "AI-recommended vendor" without checking it actually exists / is open
- Quantities from memory for unusual items (e.g., cheese for a 30-person charcuterie board — use a real calculator)
- Weather > 7 days out (highly unreliable)

### Disclaimer
This skill produces a planning *framework*. Final responsibility for:
- food safety (allergens, holding temps, raw/cooked cross-contamination)
- legal (alcohol service laws vary by jurisdiction — host's liability)
- budget overruns
- guest satisfaction

…remains with the host. The skill assumes good faith and a competent cook.
