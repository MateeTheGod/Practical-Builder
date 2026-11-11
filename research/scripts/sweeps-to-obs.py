"""Convert player-builder-sweeps.txt (FINAL values) into the #POS/#BASE delta format the fit scripts read.
Usage: python -I player-builder-sweeps-to-obs.py IN OUT"""
import sys
BASE = {
    "PG": [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99],
    "SG": [85,87,75,55,96,96,96,99,88,83,63,61,87,80,81,62,65,90,90,73,88,99],
    "SF": [95,97,95,79,88,83,81,99,84,77,75,88,95,79,77,84,85,85,84,81,96,99],
    "PF": [97,99,97,87,83,82,74,99,92,72,86,91,88,77,72,87,99,81,80,85,88,99],
    "C":  [99,97,88,99,82,81,71,99,91,61,99,95,82,71,66,96,99,69,69,95,71,99],
}
rows = {p: [] for p in BASE}
for line in open(sys.argv[1], encoding="utf-8-sig"):
    if line.startswith("#") or not line.strip():
        continue
    p = line.split()
    rid, pos, h, ws, w, a, b = p[:7]
    fin = [int(x) for x in p[7:29]]
    assert len(fin) == 22, rid
    d = [f - bb for f, bb in zip(fin, BASE[pos])]
    rows[pos].append(f"{rid} {h} {ws} {w} {a} {b} " + " ".join(str(x) for x in d))
with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as f:
    f.write("# Converted from player-builder-sweeps.txt (live game sweeps). Deltas vs each position's base.\n")
    for pos, rr in rows.items():
        f.write(f"#POS {pos}\n#BASE " + " ".join(map(str, BASE[pos])) + "\n")
        f.write("\n".join(rr) + "\n")
print({p: len(r) for p, r in rows.items()})
