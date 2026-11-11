"""Additive lookup-table model built straight from the one-input sweeps (no fitting):
FINAL = min(cap, base + dH[height] + dS[wingspan-height] + dW[weight] + dB[body] + dA[anomaly])
where each d-table is the integer change the game showed when only that input moved away from the base build.
Usage: python -I player-builder-table-model.py SWEEPS.txt [TEST OBSFILES...]  -> scores the test files."""
import sys, math, json
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
BASE = {
    "PG": [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99],
    "SG": [85,87,75,55,96,96,96,99,88,83,63,61,87,80,81,62,65,90,90,73,88,99],
    "SF": [95,97,95,79,88,83,81,99,84,77,75,88,95,79,77,84,85,85,84,81,96,99],
    "PF": [97,99,97,87,83,82,74,99,92,72,86,91,88,77,72,87,99,81,80,85,88,99],
    "C":  [99,97,88,99,82,81,71,99,91,61,99,95,82,71,66,96,99,69,69,95,71,99],
}
HREF = dict(PG=73, SG=77, SF=79, PF=81, C=84); WREF = dict(PG=180, SG=200, SF=230, PF=260, C=275)
T = {p: dict(h={}, s={}, w={}, b={}, a={}) for p in BASE}
for line in open(sys.argv[1], encoding="utf-8-sig"):
    if line.startswith("#") or not line.strip(): continue
    q = line.split(); pos = q[1]; H, WS, W, A, B = int(q[2]), int(q[3]), int(q[4]), q[5], q[6]
    fin = [int(x) for x in q[7:29]]; d = [f - b for f, b in zip(fin, BASE[pos])]
    t = T[pos]
    isH, isS, isW = WS - H == 2, H == HREF[pos], W == WREF[pos]
    if A == "None" and B == "Normal" and isW and isS: t['s'][WS - H] = (d, fin)
    if A == "None" and B == "Normal" and isW and WS - H == 2: t['h'][H] = (d, fin)
    if A == "None" and B == "Normal" and isS and WS - H == 2: t['w'][W] = (d, fin)
    if A == "None" and isS and isW and WS - H == 2 and B != "Normal": t['b'][B] = (d, fin)
    if B == "Normal" and isS and isW and WS - H == 2 and A != "None": t['a'][A] = (d, fin)
for p in T:
    z = ([0] * 22, BASE[p]); T[p]['h'].setdefault(HREF[p], z); T[p]['s'].setdefault(2, z); T[p]['w'].setdefault(WREF[p], z)
def predict(pos, H, WS, W, A, B):
    t = T[pos]; out = []; capped_in = []
    parts = [t['h'].get(H), t['s'].get(WS - H), t['w'].get(W)]
    if B != "Normal": parts.append(t['b'].get(B))
    if A != "None": parts.append(t['a'].get(A))
    if any(x is None for x in parts): return None
    for k, at in enumerate(ATTR):
        cap = 70 if (pos == "PG" and at == "ID" and A == "Def") else 99
        unsure = any(x[1][k] >= 99 for x in parts)   # a table entry itself sat at the cap
        v = BASE[pos][k] + sum(x[0][k] for x in parts)
        out.append((min(cap, max(25, v)), unsure))
    return out
if len(sys.argv) > 2:
    PG_BASE = BASE["PG"]; tot = hit = skipped = 0; off = {}; miss_rows = {}
    for fn in sys.argv[2:]:
        pos, base = ("SG" if "-SG" in fn else "PG"), PG_BASE
        for line in open(fn, encoding="utf-8-sig"):
            if line.startswith('#POS'): pos = line.split()[1]; continue
            if line.startswith('#BASE'): base = [int(v) for v in line.split()[1:]]; continue
            if line.startswith('#') or not line.strip(): continue
            q = line.split(); pr = predict(pos, int(q[1]), int(q[2]), int(q[3]), q[4], q[5])
            if pr is None: skipped += 1; continue
            for k in range(22):
                fin = base[k] + int(q[6 + k]); v, unsure = pr[k]
                if unsure or (fin >= 99 and v >= 99): continue
                tot += 1
                if v == fin: hit += 1
                else:
                    off[v - fin] = off.get(v - fin, 0) + 1
                    miss_rows.setdefault(ATTR[k], 0); miss_rows[ATTR[k]] += 1
    print(f"table model: {hit}/{tot} exact ({100*hit/tot:.1f}%), errors (pred-shown): {dict(sorted(off.items()))}; rows skipped (input outside sweeps): {skipped}")
    print("misses by attribute:", dict(sorted(miss_rows.items(), key=lambda x: -x[1])))
