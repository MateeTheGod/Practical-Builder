# Practical Builder

An attribute calculator and badge finder for the Roblox player builder. Pick a position, height, wingspan, weight, anomaly and body type, and it shows all 22 final attributes and the badges they unlock.

Open `index.html` in any browser. It's a single file with nothing to install. To host it, turn on GitHub Pages for this repo (Settings → Pages → deploy from `main`, root folder).

## Features

- **Calculator:** every position (PG, SG, SF, PF, C) with the game's real limits: height and weight ranges, wingspan from height to height + 5", all five body types, and each position's anomalies.
- **±1 flag:** marks values that sit on a rounding edge, where the game may show one higher or lower.
- **Badge Finder:** searches every legal build (about 45,000) for the badge tiers you pick.
- **Attribute limits:** in the Badge Finder, add "at least N", "at most N", "highest" or "lowest" for any attribute.

## The formula

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
