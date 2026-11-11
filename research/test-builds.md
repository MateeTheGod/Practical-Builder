# Test builds to confirm the player-builder formula
Game limits: weight ≤ 205 lb; wingspan must be from your height up to height + 5".
All builds are Point Guard and right-handed. Predictions come from `player-builder-predict.py`, refit with T1 included.
Key: `~` = rounding knife-edge, so ±1 still counts as a match. `–` = can't be predicted (capped at 99, or the effect has never been seen without the cap).

**T1 (6'2 / 6'4 / 180 / None / Normal): done.** 17/18 matched, exactly or within the expected ±1. Standing Dunk (47 vs 46) and Vertical (91 vs 90) were each off by 1. Steal read 98.

| # | Height | Wing Span | Weight | Anomaly | Body | What it tests |
|---|---|---|---|---|---|---|
| T2 | 6'6 | 6'10 | 205 | None | Normal | taller than anything in the video |
| T4 | 6'4 | 6'6 | 205 | None | Slim | Slim effects, on a build where nothing hits 99 |
| T5 | 6'4 | 6'6 | 205 | None | Narrow | Narrow effects |
| T6 | 6'4 | 6'6 | 205 | None | Built | Built effects |
| T7 | 6'4 | 6'9 | 205 | Defense | Built | Interior Defense capped at 70 under Defense? (80 if not) |
| T8 | 5'9 | 5'9 | 160 | Defense | Slim | cap vs fixed value (cap → 50, fixed → 70) |
| T9 | 6'3 | 6'7 | 205 | Post-Scoring | Narrow | do anomaly and body effects add together? |
| T10 | 6'5 | 6'9 | 205 | Finishing | Built | Finishing on a tall build |
| T11 | 6'6 | 6'6 | 160 | None | Normal | tall, shortest allowed wingspan, light |

| Attr | T2 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 |
|---|---|---|---|---|---|---|---|---|---|
| Close Shot | 90 | 87 | 87 | 87 | 82 | 72 | 93 | – | 86~ |
| Driving Layup | 93~ | 90 | 90~ | 90 | 85 | 75 | 96 | – | 90 |
| Driving Dunk | 79 | 74 | 74~ | 74~ | 72~ | 58 | 74 | 97 | 78 |
| Standing Dunk | 57~ | 50~ | 50~ | 51~ | 51 | 32 | 50 | 68 | 53 |
| Mid-Range | 86 | 90~ | 89~ | 89~ | 63~ | 72 | 97~ | 71 | 90~ |
| Three-Point | 85 | 89 | 89 | 89 | 62 | 72~ | 76 | 70 | 90 |
| Moving Shot | 85~ | 88 | 88 | 88 | 65 | 76 | 82 | 68 | 92 |
| Pass Accuracy | – | – | – | – | 87 | 91 | 89 | 81 | – |
| Ball Handle | 79 | 85~ | 86~ | 86~ | 65~ | 91 | 72 | 74~ | 93~ |
| Post Control | 68~ | 64 | 61 | 66 | 68 | 51 | 82 | 68 | 56 |
| Interior Def. | 68~ | 60~ | 58 | 64 | **70** (80 if no cap) | **50** cap / **70** fixed | 57 | 67 | 59~ |
| Perimeter Def. | 86 | 83~ | 81 | 81 | – | – | 81 | 83 | 83 |
| Lateral Quick. | 82 | 88~ | – | 83~ | 94 | 99 | – | 83 | 94 |
| Block | 68 | 61~ | 59~ | 62~ | 75~ | 54 | 59~ | 66 | 64 |
| Rebound | 60 | 56~ | 54 | 57 | 74 | 59 | 54~ | 59 | 54~ |
| Speed | 89~ | 93 | – | 91 | – | 99 | – | 96 | 93~ |
| Acceleration | 89 | 93 | 94 | 91 | 96 | 99 | 92 | 96 | 93 |
| Strength | 72~ | 69~ | 66 | 75 | 80 | 60~ | 76~ | 85 | 61 |
| Vertical | 86 | 88 | 88 | 87 | 93~ | 99 | 89 | – | 89 |

Not in the table: Free Throw and Stamina are always 99. Steal has too few points to predict (please record it anyway).

## How to judge the results
- **T2 or T11 off by 2 or more:** height effects aren't straight lines at the tall end.
- **T4–T6:** pin down the body-type effects.
- **T7 and T8:** settle the Interior Defense question under Defense.
- **Steal:** write it down on every build; each non-99 value helps.
