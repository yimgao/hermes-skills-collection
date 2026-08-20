# Default Service Schedules / 默认保养周期表

> **Authority:** Your vehicle's owner's manual is the source of truth. The intervals below are conservative defaults used when the manual is unavailable. Adjust per driving conditions.

## Driving condition classification

| Profile | Description |
|---------|-------------|
| **Normal** | Regular commuting, mostly highway, moderate climate, garage-kept, no towing |
| **Severe** | Repeated short trips <10 min, dusty/dirty roads, extreme heat or cold, towing, mountainous terrain, sustained stop-and-go, >70% city driving |

If unsure, default to **severe** — it's strictly more conservative.

---

## Engine oil & filter

| Oil type | Normal | Severe | Trigger |
|----------|--------|--------|---------|
| Conventional | 5,000 mi / 6 mo | 3,000 mi / 3 mo | mi-or-date |
| Synthetic blend | 7,500 mi / 6 mo | 5,000 mi / 6 mo | mi-or-date |
| **Full synthetic (default for 2010+)** | **10,000 mi / 12 mo** | **5,000–7,500 mi / 6 mo** | mi-or-date |

## Transmission

| Transmission | Service | Interval | Trigger |
|--------------|---------|----------|---------|
| Manual | Fluid change | 30,000–60,000 mi | mi |
| Automatic (non-sealed) | Drain & fill | 30,000–60,000 mi | mi |
| Automatic (sealed/"lifetime") | Only when contaminated | as needed | manual |
| CVT | Fluid change | 30,000–45,000 mi | mi |
| Dual-clutch (DCT) | Fluid change | 30,000 mi | mi |

## Filters

| Filter | Normal | Severe | Trigger |
|--------|--------|--------|---------|
| Engine air filter | 30,000 mi / 36 mo | 15,000 mi / 24 mo | mi-or-date |
| Cabin air filter | 15,000–20,000 mi / 24 mo | 15,000 mi / 12 mo | mi-or-date |
| Fuel filter (in-tank) | 60,000 mi / 60 mo | 30,000 mi / 36 mo | mi-or-date |
| Fuel filter (inline) | 30,000 mi / 24 mo | 15,000 mi / 12 mo | mi-or-date |

## Fluids

| Fluid | Normal | Severe | Trigger |
|-------|--------|--------|---------|
| Brake fluid | 24 mo | 24 mo | date |
| Coolant (IAT — green) | 24 mo / 24,000 mi | 12 mo | date |
| Coolant (OAT — long-life) | 60 mo / 100,000 mi | 36 mo | date |
| Power steering | 50,000 mi / 36 mo | 30,000 mi / 24 mo | mi-or-date |
| Differential (RWD/AWD) | 30,000–60,000 mi | 15,000–30,000 mi | mi |
| Transfer case (AWD/4WD) | 30,000 mi | 15,000 mi | mi |
| Windshield washer | top-off as needed | n/a | manual |

## Tires

| Service | Interval | Trigger |
|---------|----------|---------|
| Rotation | 7,500 mi (or every other oil change) | mi |
| Balance | with rotation or as needed | manual |
| Alignment | 15,000–20,000 mi or after curb hit | mi-or-event |
| New set (typical) | 40,000–60,000 mi | wear |

## Brakes

| Service | Interval | Trigger |
|---------|----------|---------|
| Pad inspection (front) | 15,000 mi or annually | mi-or-date |
| Pad replacement (front) | 25,000–65,000 mi | wear |
| Pad replacement (rear) | 30,000–80,000 mi | wear |
| Rotor replacement | every 2nd–3rd pad set | wear |
| Caliper slide grease | with pad change | manual |
| Brake fluid flush | 24 mo | date |
| Parking brake adjust | as needed | manual |

## Ignition

| Service | Interval | Trigger |
|---------|----------|---------|
| Spark plugs (copper) | 30,000 mi | mi |
| Spark plugs (platinum) | 60,000 mi | mi |
| Spark plugs (iridium — default) | 100,000 mi | mi |
| Ignition coils | replace as failed | manual |
| Drive belt (serpentine) | 60,000–100,000 mi | mi |
| Timing belt (rubber) | 60,000–100,000 mi / 84–96 mo | mi-or-date |
| Timing chain | lifetime (inspect if noisy) | manual |

## Battery & electrical

| Service | Interval | Trigger |
|---------|----------|---------|
| 12V battery test | 12 mo (6 mo severe) | date |
| 12V battery replacement | 4–6 years | age |
| Alternator test | at battery replacement | manual |
| Hybrid HV battery test | 12 mo after year 5 | date |

## HVAC & wipers

| Service | Interval | Trigger |
|---------|----------|---------|
| Cabin air filter | see Filters | mi-or-date |
| Wiper blades | 12 mo | date |
| A/C recharge | as needed (R134a / R1234yf) | manual |
| Heater core flush | 60 mo | date |

## Steering & suspension

| Service | Interval | Trigger |
|---------|----------|---------|
| Power steering fluid | see Fluids | mi-or-date |
| Tie rod ends | inspect 30,000 mi | mi |
| Ball joints | inspect 30,000 mi | mi |
| Struts/shocks | inspect 50,000 mi | mi |
| Wheel bearings | inspect 30,000 mi, repack 60,000 mi | mi |

## Exhaust

| Service | Interval | Trigger |
|---------|----------|---------|
| O2 sensors | 60,000–100,000 mi | mi |
| Catalytic converter | lifetime (unless failed) | manual |
| Muffler/exhaust pipe | inspect annually | manual |

---

## Calendar items (state-specific — verify in references/state-renewals.md)

| Item | Typical cadence | Trigger |
|------|----------------|---------|
| Registration renewal | 12 mo (some states 24 mo) | date |
| Safety inspection | 12 mo (some states 24 mo or none) | date |
| Emissions / smog | 12–24 mo (state & vehicle age dependent) | date |
| Insurance renewal | 6 or 12 mo | date |
| Extended warranty | per contract | date |
| License plate sticker | per state | date |
| Parking permit | per HOA / city | date |
| Toll transponder battery | 60 mo | date |
| Tire warranty registration | at purchase | manual |

---

## How to use this file

When registering a vehicle, the skill prompts for the driving profile (`normal` or `severe`). It then copies the corresponding intervals into `~/.hermes/cars/<nickname>/schedule.json`. The user can override any row individually.

For unknown / new EV-specific services (battery thermal management, regen brake fluid, etc.), consult the owner's manual — intervals differ sharply between Tesla, Lucid, Rivian, and traditional EVs.