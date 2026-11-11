# Player-builder attribute formulas (video 2026-11-10 22-08-11.mp4)

## What the video shows
A Roblox basketball game's **PLAYER PROFILE** builder screen (recorded with OBS). The left side has these selectors: Position, Height, Wing Span, Weight, Anomaly, Body Type and Handed. The right side lists 22 attributes, each with STARTING (always 25) and FINAL, plus a green or red number after FINAL.
- Position stays **POINT GUARD** for the whole video, and Handed stays **RIGHT**. Neither changes.
- Inputs that change: height from 5'9 to 6'4, wingspan from 5'9 to 6'8 (never below height), weight from 160 to 205, anomaly (None, Finishing, Post-Scoring, Defense) and body type (Normal, Slim, Built, Narrow).
- The green/red number is exactly **FINAL − position base**. Base is the point-guard template value, which is constant: CS 84, DL 87, DD 70, SD 45, MR 91, 3PT 91, MS 92, FT 99, PA 99, BH 94, PC 59, ID 52, PD 80, LS 91, ST 99, BL 55, RB 52, SP 95, AC 94, STR 65, VE 91, STA 99.

## The formula
```
FINAL = min(99, round( R + a·(H − 72) + b·(WS − H) + c·(W − 190) + Body + Anomaly ))
```
- H and WS are in inches; W is in lb.
- R is the FINAL value at 6'0, wingspan 6'0, 190 lb, Normal body, no anomaly, for a point guard.
- Every input adds a separate amount (they combine additively), and the total is rounded once at the end.
- Values are capped at 99. The displayed delta also uses the capped value: for example, "99 +15" means base 84 + 15 = 99.
- Least-squares fit on 51 distinct states (scripts and data are in this folder).

| Attr | R | a /in height | b /in wingspan over height | c /10 lb | Slim | Built | Narrow | Finishing | Post-Scoring | Defense | exact matches* |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Close Shot | 82.2 | +0.69 | +0.74 | +0.3 | ~0 | ~0 | ~0 | ≥ +13 (capped) | +5 | −7 | all uncensored |
| Driving Layup | 85.4 | +0.86 | +0.70 | +0.2 | ~0 | ~0 | ~0 | ≥ +10 (capped) | +5 | −7 | 1 off-by-1 |
| Driving Dunk | 66.0 | +1.66 | +1.00 | −0.6 | ~0 | ~0 | ~0 | +20 | 0 | −5 | 51/51 |
| Standing Dunk | 40.3 | +2.07 | +0.93 | 0 | ~0 | ~0 | ~0 | +14 | 0 | −2 | 48/51 |
| Mid-Range | 93.9 | −0.60 | −1.13 | 0 | ~0 | ~0 | ~0 | −16 | +9 | −23.5 | 49/51 |
| Three-Point | 93.9 | −0.64 | −1.23 | +0.1 | ~0 | ~0 | ~0 | −16 | −11 | −23 | 47/51 |
| Moving Shot | 93.1 | −0.56 | −0.80 | −0.7 | ~0 | ~0 | ~0 | −18 | −5 | −20.5 | 51/51 |
| Free Throw | always 99 | – | – | – | – | – | – | – | – | – | n/a |
| Pass Accuracy | ≥99 when no anomaly | −0.43 | 0 | −0.2 | – | – | – | Fin ≈ Def − 6 ≈ Post − 7 (only differences measurable) | | | n/a |
| Ball Handle | 97.6 | −1.52 | −1.81 | −1.4 | −0.3 | −0.1 | −0.2 | −6 | −11 | −15 | 51/51 |
| Post Control | 59.8 | +0.34 | +0.64 | +2.1 | −2 | +0.65 | −4 | 0 | +20 | 0 | 50/51 |
| Interior Def. | 50.3 | +2.17 | +0.74 | +1.5 | −3 | +1 | −5 | 0 | 0 | **+14.5, then capped at 70** (confirmed by T7/T8) | 54/55 |
| Perimeter Def. | 77.8 | +0.96 | +0.64 | +0.1 | +0.4 | −2.2 | −2.2 | 0 | 0 | +19 (seen uncapped in T8) | 55/55 |
| Lateral Quick. | 88.6 | −0.48 | 0 | −2.6 | +4.6 | +0.6 | ≥ +7 (capped) | 0 | 0 | +10.5 | 2 off-by-1 |
| Steal | ≥99 mostly | ≈ −1.9 | ≈ +3.8 | ≈ −1 | | | | | | | only 4 points (unreliable) |
| Block | 50.7 | +2.19 | +1.02 | 0 | 0 | 0 | −2 | 0 | 0 | +10 | 51/51 |
| Rebound | 50.0 | +1.04 | +0.79 | +0.6 | −1 | 0 | −2.7 | 0 | 0 | +15 | 48/51 |
| Speed | 94.7 | −0.73 | 0 | −1.1 | +3 | +0.8 | ≥ +4 (capped) | +6 | −2 | +6 (seen in T7) | all uncensored |
| Acceleration | 94.5 | −0.74 | 0 | −0.9 | +2.4 | +0.5 | +3.5 | +6 | −2 | +5.6 | 50/51 |
| Strength | 66.9 | +0.29 | 0 | +2.45 | −3.3 | +2.9 | −6 | +10 | +10 | +5 | 49/51 |
| Vertical | 90.7 | −0.66 | +0.08 | −0.7 | +1 | −0.5 | +1 | ≥ +8 (capped) | 0 | +5.7 | 1 off-by-1 |
| Stamina | always 99 | – | – | – | – | – | – | – | – | – | n/a |

\*In the exact-match column, misses are off by 1 and come from rows where the fit predicts .45–.65 (a rounding knife-edge), or from a possible misread. "capped" means every observation in that group reads 99, so the true effect is only known to be at least the value shown. "~0" means the fitted effect is below 0.3 and not measurable here.

### How to read the numbers
- **Height** helps dunks, block, interior defense and rebound, by about 1–2.2 per inch. It hurts shooting, handle and physicals, by about 0.5–1.5 per inch.
- **Wingspan above height** helps finishing and defense, by about 0.6–1 per inch. It hurts shooting (−0.8 to −1.2) and handle (−1.8).
- **Weight** helps strength (+2.45 per 10 lb), post control (+2.1) and interior defense (+1.5). It hurts lateral quickness (−2.6), handle (−1.4), speed (−1.1) and acceleration (−0.9).
- **Anomalies** are fixed integer bonuses and penalties, and they add independently of height, wingspan and weight. This holds wherever they could be checked: the anomaly-minus-None difference stays constant across builds, apart from ±1 rounding.
- **Body types** are small constant offsets, mostly on post control, interior defense, lateral quickness, rebound and the physicals.

## Body-type offsets (refit after in-game tests T4–T6; these replace the body columns above)
Compared with Normal. Body type has **no effect** on finishing, shooting, Ball Handle, Pass or Steal: at 6'4 / 6'6 / 205, all four body types show identical values for those.

| Attr | Slim | Built | Narrow |
|---|---|---|---|
| Post Control | −1.8 | +0.6 | −4.5 |
| Interior Def. | −3.0 | +1.3 | −5.1 |
| Perimeter Def. | +0.3 | −2.2 | −2.1 |
| Lateral Quick. | +4.9 | +0.4 | **+10.1** |
| Block | 0 | 0 | −2.3 |
| Rebound | −1.2 | +0.2 | −2.6 |
| Speed | +2.9 | +0.9 | +4.8 |
| Acceleration | +2.3 | +0.4 | +3.8 |
| Strength | −3.3 | +2.9 | −6.0 |
| Vertical | +0.9 | −0.5 | +0.9 |

The game always rounds once on the total (see Rounding below), so these fractional offsets are fine. Built's values here are the model's best estimates. For example, in T6 Built showed Lateral −8 against −3 for Slim and +2 for Narrow.

## Shooting Guard (video 2026-11-10 22-41-06.mp4, 19 distinct states)
- The SG weight slider goes up to **225** (PG maxes out at 205). Heights seen: 6'3–6'8. Wingspans seen: height to height+5.
- SG base row (FINAL − delta): CS 85, DL 87, DD 75, SD 55, MR 96, 3PT 96, MS 96, FT 99, PA 88, BH 83, PC 63, ID 61, PD 87, LS 80, ST 81, BL 62, RB 65, SP 90, AC 90, STR 73, VE 88, STA 99.
- **Same formula.** The fit reproduces every SG observation, with 7 of 380 values off by 1 (`python -I player-builder-fit.py player-builder-observations-SG.txt 99`).
- **Effects that carry over from PG:** wingspan over height, weight, body-type offsets and Post-Scoring. These match PG to within about ±0.3. Examples: per inch of wingspan over height, Mid-Range −1.14 for both positions and Ball Handle −1.75 (SG) vs −1.80 (PG); Strength changes +0.24 per lb for both; Narrow gives Lateral Quickness about +9–10 for both.
- **Effects that differ by position:**
  - Height slopes are larger for SG. Per inch, SG vs PG: Close Shot +1.75 vs +0.71, Driving Dunk +2.8 vs +1.7, Rebound +3.4 vs +1.0, Perimeter Defense +2.2 vs +1.0, shooting about −1.0 vs −0.6.
  - The Defense anomaly's penalties differ too. SG vs PG: Close Shot −10 vs −7, Driving Dunk −10 vs −5, Ball Handle −17.6 vs −14.8. These SG estimates come only from Narrow builds.
- **Interior Defense under Defense is *not* capped at 70 for SG:** it reads 72–76, which is no-anomaly Interior Defense + about 14.6. So the 70 cap is specific to PG, probably a per-position cap.
- **Steal (finally measurable, SG):** −2.2 per inch of height, +2.7 per inch of wingspan over height, about 0 for weight, and +10.7 with the Defense anomaly. It fits all 19 SG states exactly.

## All five positions (video 2026-11-10 22-45-30.mp4 adds SF, PF, C)
Data: `player-builder-observations-SF-PF-C.txt`. To fit any position file: `python -I player-builder-fit-multi.py <file>`.
Fit quality on values below the 99 cap: **SF 226/227, PF 269/271, C 273/275 reproduced exactly**. Every miss is off by 1.

**General formula (every position):**
```
FINAL = min(cap, round( Base_pos + a_pos·(H − Href_pos) + b·(WS − H − 2) + c·(W − Wref_pos) + Body + Anomaly_pos ))
```
Each position has a **reference build**: wingspan is height + 2", and every delta is 0 there, so Base is FINAL at that build.

| Pos | Reference build | Max weight seen | Base row CS DL DD SD · MR TP MS FT · PA BH PC · ID PD LS ST BL RB · SP AC STR VE STA |
|---|---|---|---|
| PG | 6'1 / 6'3 / ~180 (from the fit) | 205 | 84 87 70 45 · 91 91 92 99 · 99 94 59 · 52 80 91 99 55 52 · 95 94 65 91 99 |
| SG | 6'5 / 6'7 / 200 | 225 | 85 87 75 55 · 96 96 96 99 · 88 83 63 · 61 87 80 81 62 65 · 90 90 73 88 99 |
| SF | 6'7 / 6'9 / 230 | 230 | 95 97 95 79 · 88 83 81 99 · 84 77 75 · 88 95 79 77 84 85 · 85 84 81 96 99 |
| PF | 6'9 / 6'11 / 260 | 290 | 97 99 97 87 · 83 82 74 99 · 92 72 86 · 91 88 77 72 87 99 · 81 80 85 88 99 |
| C | 7'0 / 7'2 / 275 | 310 | 99 97 88 99 · 82 81 71 99 · 91 61 99 · 95 82 71 66 96 99 · 69 69 95 71 99 |

**Effects that are the same for every position** (within ±0.3):
- **b, per inch of wingspan over height:** CS +0.6–0.75, DL +0.5–0.8, DD +1.0, SD +0.75–1.0, MR −1.1, 3PT −1.2 to −1.35, MS −0.65 to −0.9, BH −1.5 to −1.85, PC +0.6–0.75, ID +0.7–0.8, PD +0.55–0.65, **ST +2.7–3.0**, BL +1.0, RB +0.8. Physicals ≈ 0.
- **c, per lb:** STR +0.20 to +0.25, PC +0.16 to +0.21, ID +0.08 to +0.15, LS −0.16 to −0.27, BH −0.05 to −0.15, SP −0.08 to −0.18, AC −0.02 to −0.17. **Center Stamina −0.06**: Stamina drops below 99 for heavy Centers.
- **Body type** (vs Normal): Slim, Built and Narrow as in the PG table above (Narrow LS +9.3 to +10 at every position). **Bulky** (PF, C): STR +7, PC +4.7, ID +3.6 to +3.9, SD +3.5 to +4, DD +1 to +2, PD −3, SP −3.9, AC −5.1 to −5.4, VE −1.9, Stamina −1 (C).

**Effects that differ by position:**
- **a, per inch of height:**

| Attr | PG | SG | SF | PF | C |
|---|---|---|---|---|---|
| CS | +0.7 | +1.75 | +1.4 | +1.6 | ≥ (capped) |
| DD | +1.7 | +2.8 | +2.0 | +1.4 | −1.5 (only 7'0 and 7'2 seen) |
| SD | +2.1 | +2.75 | +2.6 | +3.0 | +3 |
| MR / 3PT | −0.6 | −1.0 | −1.45 / −1.25 | −1.2 / −1.35 | −1.0 / −1.3 |
| BH | −1.5 | −1.4 | −1.25 | −0.8 | −2.4 |
| ID | +2.1 | +2.5 | +1.7 | +2.3 | +2.0 |
| PD | +1.0 | +2.2 | +2.1 | +2.3 | −1.35 |
| ST | ? | −2.2 | −2.25 | −2.2 | −2.2 |
| BL | +2.2 | +3.2 | +3.3 | +3.7 | +2.5 |
| RB | +1.0 | +3.4 | +2.5 | capped | capped |
| SP / AC | −0.7 / −0.8 | −0.6 / −0.4 | −0.65 / −0.65 | −0.5 / −1.0 | −0.8 / −0.55 |
| STR / VE | +0.3 / −0.6 | +0.6 / −0.4 | +0.65 / −1.3 | +0.5 / −0.9 | capped / −1.1 |

- **Anomalies:**

| Anomaly | Seen on | Main bonuses | Main penalties |
|---|---|---|---|
| Finishing | PG | DD +20, SD +14, STR +10, SP/AC +6 | shooting −16 to −18, PA about −16, BH −6 |
| Post-Scoring | PG, SG | PC +20, STR +10, CS/DL +5, MR +9 | 3PT −11/−12, MS −5, BH −11, PA −14 (SG), SP/AC −2 |
| Defense | PG, SG | ID +14.5, PD +19, BL +10, LS +9–10.5, ST +10.7 (SG), RB +15 (PG) / +6 (SG), SP/AC/VE +4–6, STR +5 | shooting −22/−23, BH −15/−17.6, CS −7/−10, DD −5/−10 |
| Playmaking | SF, PF, C | PA +12 (or capped), BH +13 (SF) / +11.7 (PF) / +18.5 (C), PC +3, SP/AC +2–3 (+7 on C) | SF: finishing/defense −5 to −12; PF: about −5 almost everywhere; C: shooting −6.5, DD −8 |
| Shooting | PF, C | MR/3PT/MS +11 to +12.4 (PF), +9.6 to +11 (C) | finishing/defense about −7 to −12, PA −4 (PF) / −9 (C), BH −3 (PF) / −9 (C), SP/AC −7 (C) |
| Agility | C | SP +12.2, AC +12.2, LS +10.2, VE +7.4 | shooting/PA about −5, BH −3.8, DD −3 |

- **Caps:** 99 everywhere, except PG Interior Defense under Defense, which caps at 70 (SG reached 76). Several C attributes (CS, SD, PC, RB, STR) sit at 99 in every state, so their slopes are unknown.

## Live one-setting-at-a-time sweeps (computer use, 2026-11-10)
- Data: `player-builder-sweeps.txt` holds FINAL values; `player-builder-observations-sweeps.txt` holds the same as deltas. There are 155 states across all five positions: every weight from minimum to maximum in 5 lb steps, every height (wingspan = height+2), every wingspan at base height, all five body types, and every anomaly the position offers.
- **Real limits:** PG 5'9–6'6, 160–205 lb. SG 6'3–6'8, 180–225. SF 6'5–6'10, 200–260. PF 6'7–7'0, 230–290. C 6'9–7'3, 245–310. Wingspan runs from height to height+5". Base builds: PG 6'1/6'3/180, SG 6'5/6'7/200, SF 6'7/6'9/230, PF 6'9/6'11/260, C 7'0/7'2/275.
- **Every position offers all five body types** (Normal, Built, Bulky, Narrow, Slim). Anomalies per position: PG and SG get Post-Scoring, Defense and Finishing. SF and PF get Shooting and Playmaking. C gets Shooting, Playmaking and Agility.
- **The exact formula wasn't found.** A straight-line model fits 97% of all 5,110 values, and 5-fold cross-validation scores it 87.7% on held-out data. Adding interactions (height×weight, anomaly×inputs, body×inputs) did *worse*. Rounding each input's effect separately did much worse (62%). The leftover ±1 errors don't follow a simple pattern; they may come from a nonlinear curve the game uses, or from misreads in the older lower-zoom video data.
- The calculator uses the full-data model (96.2% exact). It marks ±1 when the formula lands within 0.15 of .5, which catches 89% of the misses.

## Rounding
The data fits a model where every term is a fractional value, the sum is rounded once, and then the cap applies. Rounding each term separately does not fit. For example, the Finishing bonus on Standing Dunk shows as +13 or +14 depending on the build. Round-half-up and floor cannot be told apart, because the intercept absorbs the 0.5 offset.

## Still ambiguous or untested
- ~~Interior Defense + Defense anomaly~~ **Resolved:** Defense adds about +14.5 to Interior Defense, then caps it at 70. T8 (5'9 / 5'9 / 160 / Defense / Slim) showed 51, not 70.
- **In-game checks so far:** T1 16/18, T7 17/17, T2 17/19, T8 16/18, T4 17/18, T5 16/17 and T6 16/18, so 115/125 predictions matched, counting ±1 where the prediction sat on a rounding edge. Each of the 10 misses was off by exactly 1. All test builds are now in `player-builder-observations.txt` and the fit.
- Free Throw, Stamina and, with no anomaly, Pass and Steal are always 99. Their formulas can't be seen in this recording.
- The finishing bonus on Close Shot and Layup, the Defense bonus on Perimeter Defense, and Narrow on Lateral Quickness and Speed are hidden by the 99 cap.
- Narrow has 2 observations and Slim has 3, so their offsets are rough (±1).
- Only point guard and right-handed were shown. Other positions presumably change the base row, and the slopes may differ too.
- The slopes come from narrow ranges (height 69–76 in, wingspan 69–80 in, weight 160–205 lb), so they're fitted to about ±0.1–0.2 per unit. Behaviour outside those ranges, and any lower cap (minimum 25?), is unknown.
- A few frames had Roblox player-list or quick-chat overlays on the panel. A small number of 1-off misses may be misreads rather than model error.

## Files (this folder)
- `player-builder-observations.txt`: every distinct state read (inputs plus 22 deltas), which is the evidence table.
- `player-builder-fit.py`: least-squares fit plus an exact-match check (`python -I player-builder-fit.py player-builder-observations.txt`).
