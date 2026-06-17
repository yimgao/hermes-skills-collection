---
name: travel-itinerary-planner
description: "Use when planning a trip — generates day-by-day itineraries with attractions, restaurants, logistics, and budgeting for any destination."
version: 1.0.0
author: yimgao
license: MIT
metadata:
  hermes:
    tags: [travel, itinerary, planning, lifestyle, trip, vacation, travel-guide]
    related_skills: []
---

# Travel Itinerary Planner

> Generate a day-by-day travel itinerary for any destination. Researches attractions, restaurants, transportation, and practical tips — delivers a complete trip plan with timing, budget estimates, and local insights.

---

## Overview

This skill creates a comprehensive travel itinerary for any destination. Given a city, duration, and preferences, it researches top attractions, dining options, logistics, and local tips, then compiles everything into a structured day-by-day plan.

The output balances must-see landmarks with local gems, realistic timing, meal suggestions, and practical logistics — so the user can hit the ground running without spending hours on research.

**What it covers:**
| Category | Details |
|----------|---------|
| **Attractions** | Must-see sights, hidden gems, free activities |
| **Dining** | Breakfast/lunch/dinner, local cuisine, price ranges |
| **Logistics** | Getting around, best times, ticket booking |
| **Budget** | Estimated daily costs (low/mid/premium) |
| **Tips** | Local customs, safety, packing, language |
| **Alternative plans** | Rainy day, half-day, family-friendly options |

---

## When to Use

- User asks: *"Plan a 3-day trip to Tokyo"*
- User asks: *"I'm going to Paris for 5 days with my family — what should we do?"*
- User asks: *"Help me plan a budget backpacking trip through Thailand"*
- User asks: *"What's a good one-day itinerary in Shanghai?"*
- User asks: *"I have 2 days in Singapore — make the most of it"*

---

## Core Workflow

### Step 1: Gather Requirements

Clarify (or infer) the trip details:

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `destination` | ✅ Yes | City or region | — |
| `days` | ✅ Yes | Number of days | — |
| `travel_style` | ❌ No | Budget / Mid-range / Premium / Backpacker | Mid-range |
| `interests` | ❌ No | Food / History / Nature / Shopping / Nightlife | Mixed |
| `with_kids` | ❌ No | Family-friendly? | No |
| `arrival_time` | ❌ No | Day 1 arrival time | Morning |
| `departure_time` | ❌ No | Last day departure time | Evening |

If the user provides only a destination and days, assume mixed interests + mid-range budget.

### Step 2: Research Destination

Use web search to gather comprehensive info about the destination:

**Essential searches:**
```
"{destination} top attractions"
"{destination} best restaurants local cuisine"
"{destination} day by day itinerary"
"{destination} things to do in {days} days"
"{destination} travel tips 2026"
"{destination} hidden gems off the beaten path"
```

**For each day's area/neighborhood, search specifically:**
```
"{destination} {neighborhood} best things to do"
"{destination} {neighborhood} restaurants"
```

**Logistics research:**
```
"{destination} public transportation"
"{destination} getting around"
"{destination} best area to stay"
"{destination} sim card wifi"
```

### Step 3: Build Itinerary

Organize the day-by-day plan. A good itinerary has:

- **Realistic pacing** — 3-4 activities per day max, not an exhausting checklist
- **Geographic clustering** — activities near each other, not criss-crossing the city
- **Built-in flexibility** — buffer time for wandering, rest, unexpected finds
- **Meal anchors** — suggest breakfast, lunch, and dinner spots near each day's route
- **Logistics notes** — how to get between locations, ticket booking tips

### Step 4: Generate Report

Use the following template:

```markdown
# Travel Itinerary: {Destination}

**Duration:** {N} days
**Travel Style:** {Budget / Mid-range / Premium}
**Interests:** {Food / History / Nature / Shopping / Nightlife}
**Travelers:** {Solo / Couple / Family with kids / Group}
**Dates:** {optional: specific dates}

---

## 📋 Quick Overview

| Day | Theme | Key Activities | Est. Cost (per person) |
|-----|-------|----------------|----------------------|
| 1 | {Arrival & explore} | {highlights} | ${N} |
| 2 | {Main sightseeing} | {highlights} | ${N} |
| 3 | {Culture & food} | {highlights} | ${N} |
| {N} | {Departure} | {highlights} | ${N} |

**Total estimated budget:** ${N}-${N} per person (excl. flights/hotel)

---

## 🗺️ Pre-Trip Essentials

### Best Time to Visit
- {Seasonal recommendation}
- {Weather notes}

### Where to Stay (Recommended Areas)
| Area | Vibe | Best For | Price Range |
|------|------|----------|-------------|
| {Area 1} | {description} | {type of traveler} | {$$/$$$/$$$$} |
| {Area 2} | {description} | {type of traveler} | {$$/$$$/$$$$} |

### Getting Around
- {Transport option 1} — {cost}, {time}, {tip}
- {Transport option 2} — {cost}, {time}, {tip}

### Booking Tips
- {e.g., "Book Ghibli Museum tickets 1 month in advance"}
- {e.g., "Skip-the-line passes for Louvre worth it"}

---

## 📅 Day-by-Day Itinerary

---

### Day 1: {Theme / Title}

**📍 Area:** {Neighborhood(s)}

| Time | Activity | Details | Duration | Cost |
|------|----------|---------|----------|------|
| 09:00 | 🥐 **{Breakfast}** | {Restaurant name + dish suggestion} | 45 min | ${N} |
| 10:00 | 🏛️ **{Attraction 1}** | {What it is + why go + booking tip} | 2 hrs | ${N} |
| 12:30 | 🍜 **{Lunch}** | {Restaurant name + what to order} | 1 hr | ${N} |
| 14:00 | 🚶 **{Attraction 2}** | {Nearby — walking distance from lunch} | 1.5 hrs | ${N} |
| 15:30 | ☕ **{Coffee / Rest}** | {Cafe recommendation} | 30 min | ${N} |
| 16:00 | 🛍️ **{Activity 3}** | {Shopping / stroll / museum} | 2 hrs | ${N} |
| 18:30 | 🍽️ **{Dinner}** | {Restaurant + what to order} | 1.5 hrs | ${N} |
| 20:00 | 🌙 **{Evening}** | {Nightlife /夜景 / bar / walk} | — | ${N} |

**🚇 Getting around today:** {Transport tips for this day's route}

**💡 Pro tip:** {Local insight for this day}

---

### Day 2: {Theme / Title}
[Same structure as Day 1]

---

[Continue for remaining days...]

---

## 🍽️ Food Guide

### Must-Try Local Dishes
| Dish | Where to Try | Price | Description |
|------|-------------|-------|-------------|
| {Dish 1} | {Restaurant} | ${N} | {what makes it special} |
| {Dish 2} | {Restaurant} | ${N} | {what makes it special} |

### Dietary Options
- **Vegetarian/Vegan:** {recommendations if applicable}
- **Food allergies:** {local phrases / precautions}

---

## 💰 Budget Breakdown (per person)

| Category | Budget | Mid-Range | Premium |
|----------|--------|-----------|---------|
| 🏨 Accommodation (per night) | ${N} | ${N} | ${N} |
| 🍜 Food (per day) | ${N} | ${N} | ${N} |
| 🚇 Transport (per day) | ${N} | ${N} | ${N} |
| 🎟️ Attractions (total) | ${N} | ${N} | ${N} |
| **Daily total** | **${N}** | **${N}** | **${N}** |

---

## 🎒 Packing & Preparation Checklist

- [ ] {Visa / passport validity check}
- [ ] {Travel insurance}
- [ ] {SIM card / eSIM / pocket wifi}
- [ ] {Power adapter type}
- [ ] {Weather-appropriate clothing}
- [ ] {Comfortable walking shoes}
- [ ] {Translation app / phrase book}
- [ ] {Local currency / payment methods}
- [ ] {Emergency numbers}

---

## 🌦️ Alternative Plans

### Rainy Day Option
- {Indoor alternatives if weather is bad}

### Half-Day (if tired)
- {Condensed version of the day}

### Family-Friendly Modifications
- {Changes if traveling with kids}

---

## 📋 Sources

- {Source URL 1}
- {Source URL 2}
- {Source URL 3}
```

---

## Example Invocations

### Example 1: Full trip plan
```
User: Plan a 4-day trip to Kyoto. Mid-range budget, interests include food, temples, and nature.
Hermes should:
  1. Search: "Kyoto 4 day itinerary"
  2. Search: "Kyoto best restaurants local cuisine"
  3. Search: "Kyoto temples must see"
  4. Search: "Kyoto hidden gems nature"
  5. Search: "Kyoto getting around transportation"
  6. Compile day-by-day plan
  7. Save to ~/travel/kyoto/2026-06-17-4day-itinerary.md
```

### Example 2: Quick one-day plan
```
User: I have one day in Shanghai. What should I do?
Hermes should:
  1. Search: "Shanghai one day itinerary"
  2. Search: "Shanghai best food this area"
  3. Create a condensed single-day plan
  4. Prioritize the must-sees
```

### Example 3: Budget backpacking
```
User: Plan a cheap 7-day trip to Thailand (Bangkok + Chiang Mai)
Hermes should:
  1. Search budget travel resources
  2. Focus on free/cheap activities
  3. Suggest budget accommodation and street food
  4. Include transport costs between cities
```

---

## Common Pitfalls

| # | Problem | Solution |
|---|---------|----------|
| 1 | **Over-scheduling.** | 3-4 activities per day max. Include buffer time. A relaxed traveler enjoys more. |
| 2 | **Unrealistic transit times.** | Always check travel time between locations. Add 15-20% buffer for navigation/walking. |
| 3 | **Ignoring opening hours / closures.** | Check if attractions are closed on certain days (many museums close Monday). |
| 4 | **Assuming same interests.** | If user hasn't specified, offer a balanced mix: culture + food + nature + shopping. |
| 5 | **Generic restaurant picks.** | Be specific — "Ramen at Ichiran Shibuya" not "try local ramen". Name, dish, location. |
| 6 | **No alternative plan.** | Always include rainy day and half-day options. Things change. |
| 7 | **Outdated prices.** | Note that prices are estimates based on recent research. Recommend checking official sites. |
| 8 | **Forgetting jet lag.** | Day 1 should be lighter. Don't schedule a 7 AM temple visit after a 14-hour flight. |

---

## Verification Checklist

- [ ] Destination, duration, and travel style confirmed
- [ ] Top attractions researched with opening hours
- [ ] Restaurant recommendations specific (name + dish)
- [ ] Transit logistics between activities verified
- [ ] Day-by-day plan with realistic timing (3-4 activities/day)
- [ ] Budget estimate per day (low/mid/premium)
- [ ] Pre-trip essentials covered (visa, SIM, transport pass, area to stay)
- [ ] Alternative plans included (rainy day, half-day)
- [ ] Packing checklist provided
- [ ] Saved to `~/travel/{destination}/`


---

## 📋 Data Sources & Accuracy

This skill relies on searching external data. Follow these guidelines to ensure accuracy:

### Primary vs Secondary Sources
| Priority | Source Type | Examples |
|----------|-------------|----------|
| 🥇 **Primary (prefer)** | Government / Official | Census.gov, BLS, city economic dev, official APIs |
| 🥈 **Secondary** | Aggregators / Reviews | Google Maps, Yelp, LoopNet, Wikipedia |
| 🥉 **Tertiary** | Estimates / Inferences | Industry reports, blog posts, news articles |

### Accuracy Rules
1. **Always cite the source** for each data point — don't state numbers without attribution
2. **When sources conflict**, prefer: government > official > aggregator > blog
3. **If data is unavailable**, say "Not found" — do NOT fabricate or approximate without stating it's an estimate
4. **Mark estimates clearly** with "~" or "estimated" — never present guesses as facts
5. **Use ranges** when uncertain (e.g., "$20-25/sqft" not "$22.50/sqft")
6. **Timestamp your data** — note when it was collected (e.g., "as of June 2026")

### When Web Search Returns Limited Data
- Note the limitation explicitly: "Google Maps limited view", "Search blocked by CAPTCHA"
- Fall back to known data or general market knowledge
- Explicitly mark knowledge-based data as "based on general market knowledge"
- Never invent competitor names, ratings, or prices

### Verification Checklist
- [ ] Every number attributed to a source
- [ ] Estimates clearly marked (use "~" or "estimated")
- [ ] Unavailable data noted as "not found"
- [ ] Data collection timestamp recorded
- [ ] Confidence level noted (High / Medium / Low)
