# Independent PBLab cap comparison

The fixture in `data/pblab-validation.json` provides a reproducible comparison with PB Build Lab's recorded Player Profile readings. It contains 69 distinct profiles and 1,518 FINAL ratings, observed on November 3, 8 and 9, 2026. It has not been used to refit this repository's model.

Run with Node.js 18 or later, without installing packages:

```sh
node research/scripts/check-pblab.cjs --summary
```

Omit `--summary` to include every mismatch, its signed prediction error, rounding marker, alternative value and source references. The script executes the calculator's existing `compute()` section in `src/template.html` with `src/model.json`; it does not maintain another formula implementation or run the page UI. Invalid fixture data, changed attribute order, duplicate profiles and changed extraction boundaries fail explicitly. Prediction differences are diagnostics and do not fail the command.

## Baseline

Against model/calculator commit `c13db5303552ee415a0df2b0460ca92b6e185e4d`:

| Metric | Result |
| --- | ---: |
| Distinct profiles | 69 |
| FINAL ratings | 1,518 |
| Exact predictions | 1,441 (94.93%) |
| Predictions within one point | 1,518 |
| Largest absolute difference | 1 |
| Mismatches without a rounding marker | 12 |

The fixture contains 60 PG height/wingspan profiles, the other four position defaults, three additional Center height profiles, and two Center Shooting/body-type profiles. PG and Center defaults already present elsewhere are stored once with their source references combined. All five position defaults reproduce exactly.

## Provenance and scope

Each entry records position, height and wingspan in inches, weight in pounds, anomaly/body type codes used by this calculator, handedness, observation date, starting rating, game version status, and source filenames. The shared `attributeKeys` and `attributeNames` arrays define the order of the 22 FINAL values in `observed`. Starting ratings were 25. The game did not display a version number.

Source records from PBLab:

- `pg-height-wingspan-2026-11-09.json`: 60 screenshot transcriptions at 180 lb, Normal, None, Right. Each entry retains its individual Roblox screenshot filename.
- `position-defaults-2026-11-03.json`: all five defaults, Normal, None, Right.
- `center-height-caps-2026-11-08.json`: 6'10 through 7'1 at fixed 7'2 wingspan and 275 lb, Normal, None, Right.
- `center-body-type-samples-2026-11-08.json`: Slim/Normal at 7'0 height, 7'0 wingspan, 270 lb, Shooting, **Left**. The calculator has no handedness input; these comparisons cannot isolate a handedness effect.

The source JSON records and original screenshots remain in PBLab; filenames here identify those records, not files bundled in this repository. The fixture is a transcription export, not another live verification. Its export date is separate from the observation dates.

Two old PG transcriptions were corrected by inspecting the original screenshots on November 11 before export:

| Screenshot | Profile | Attribute | Old | Corrected FINAL |
| --- | --- | --- | ---: | ---: |
| `RobloxScreenShot20261109_172118406.png` | PG, 5'10 / 6'3 / 180, None, Normal, Right | Rebound | 53 | 51 |
| `RobloxScreenShot20261109_172226288.png` | PG, 6'6 / 6'9 / 180, None, Normal, Right | Moving Shot | 89 | 88 |

Twenty-one cases in the original comparison overlap the raw upstream `data/sweeps.txt` and agree after those corrections; that count includes repeated baseline cases before deduplication. Independent collection does not mean all physical profiles were unseen during model fitting. Keep this fixture outside the training inputs while using it to compare model changes; if it is later used in training, retain another validation set.

This comparison concerns maximum caps only. It does not verify badge thresholds, attribute upgrade links, allocation costs, or 99 OVR feasibility. Unmarked predictions remain estimates; the rounding heuristic does not identify every one-point error.
