# Practical Builder

An attribute cap calculator and badge finder for the Roblox player builder. Pick a position, height, wingspan, weight, anomaly and body type to see 22 predicted maximum caps and potential badge eligibility. These predictions do not establish an attribute allocation achievable at 99 OVR; confirm that allocation in the game creator. Badge names and thresholds are community-reported and unverified in the current game.

Open `index.html` in any browser. It's a single file with nothing to install. To host it, turn on GitHub Pages for this repo (Settings → Pages → deploy from `main`, root folder).

## Features

- **Calculator:** every position (PG, SG, SF, PF, C) with the game's real limits: height and weight ranges, wingspan from height to height + 5", all five body types, and each position's anomalies.
- **±1 flag:** marks values that sit on a rounding edge, where the game may show one higher or lower.
- **Badge Finder:** searches every legal build (about 45,000) for the badge tiers you pick.
- **Attribute limits:** in the Badge Finder, add "at least N", "at most N", "highest" or "lowest" for any attribute.
- **Threshold Optimizer:** after selecting a physical profile, click **Optimize this profile**. Choose badge tiers, keep any gameplay minimum ratings (for example Free Throw), and view the smallest total rating increase that meets the targets. AND/OR rules and shared attribute requirements are solved jointly. Finder badge picks can be imported. The plan includes all 22 ratings, the requirements keeping them there, extra badge eligibility, a lower-cap rounding option and a copy action. Unreachable targets are reported explicitly. Targets and minimums stay saved in the browser.
- **Separate tools:** Calculator, Optimizer and Badge Finder each have their own panel. Switch tabs with Left/Right, Home or End; Tab moves into the selected panel.
- **Search freshness:** results retain a summary of the requirements used. Changing position, dunk interpretation, badge picks or attribute limits marks results outdated and disables Open until you search again or restore those requirements. Attribute limits apply to predicted caps, not allocated ratings.

## The formula

The optimizer minimizes the sum of rating increases from 25 under the selected cap predictions and community badge rules. It does not model the game's rating links, actual upgrade costs, available allocation or OVR. Ratings without a target or user minimum stay at 25; this is a threshold worksheet, not a complete gameplay build. No shared 500-point budget is assumed. Run `node research/scripts/check-threshold-planner.cjs` for solver checks, exhaustive small-case comparisons and actual badge/profile cases.

```
FINAL = min(cap, round(base + h·(height − ref height) + w·(wingspan − height − 2)
                      + c·(weight − ref weight) + body offset + anomaly))
```

Each position has its own base row, slopes and anomaly values. The cap is 99, except Interior Defense with the Defense anomaly at PG, which is capped at 70.

| Position | Reference build | Height | Weight |
|---|---|---|---|
| PG | 6'1, WS 6'3, 180 lb | 5'9–6'6 | 160–205 |
| SG | 6'5, WS 6'7, 200 lb | 6'3–6'8 | 180–225 |
| SF | 6'7, WS 6'9, 230 lb | 6'5–6'10 | 200–260 |
| PF | 6'9, WS 6'11, 260 lb | 6'7–7'0 | 230–290 |
| C | 7'0, WS 7'2, 275 lb | 6'9–7'3 | 245–310 |

The model was fitted to 5,110 recorded values. It matches 96–97% of them exactly, and nearly all the rest are off by 1. Height, wingspan and weight each change attributes in a straight line on their own. The leftover ±1 errors only appear when several settings change at once. Details are in [`research/formulas.md`](research/formulas.md).

## Repo layout

| Path | What it is |
|---|---|
| `index.html` | The built calculator |
| `src/template.html` | Page source; `/*MODEL*/` is replaced by the model |
| `src/model.json` | Fitted coefficients |
| `src/build.py` | Rebuilds `index.html` (`python src/build.py`) |
| `research/data/` | Recorded attribute values (video reads and one-setting-at-a-time sweeps) |
| `research/scripts/` | Fitting, cross-validation and evaluation scripts (plain Python, no dependencies) |
| `research/formulas.md` | Full write-up of the findings |

To refit the model and rebuild the page:

```
python research/scripts/export-model.py src/model.json research/data/observations.txt research/data/observations-SG.txt research/data/observations-SF-PF-C.txt research/data/observations-sweeps.txt
python src/build.py
```

Badge thresholds come from a community badge sheet. "/" means either option counts, and "&" means both are needed.
