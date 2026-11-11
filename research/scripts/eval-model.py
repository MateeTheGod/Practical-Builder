"""Score a model.json against observation files (exact-match count on values below the cap).
Usage: python -I player-builder-eval-model.py MODEL.json OBSFILE..."""
import sys, json, math
m = json.load(open(sys.argv[1]))
ATTR = m['attrs']
PG_BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
tot = hit = 0; off = {}
for fn in sys.argv[2:]:
    pos, base = ("SG" if "-SG" in fn else "PG"), PG_BASE
    for line in open(fn, encoding="utf-8-sig"):
        if line.startswith('#POS'): pos = line.split()[1]; continue
        if line.startswith('#BASE'): base = [int(v) for v in line.split()[1:]]; continue
        if line.startswith('#') or not line.strip(): continue
        p = line.split(); H, WS, W, A, B = int(p[1]), int(p[2]), int(p[3]), p[4], p[5]
        P = m['positions'][pos]
        for k, at in enumerate(ATTR):
            fin = base[k] + int(p[6 + k])
            c = P['coef'][at]
            x = c['I'] + c['h'] * (H - P['href']) + c['w'] * (WS - H - 2) + c['c'] * (W - P['wref'])
            if B != 'Normal': x += (P.get('body', {}).get(at, {}) or {}).get(B, m['bodyOffsets'][at].get(B, 0)) if P.get('body') else m['bodyOffsets'][at].get(B, 0)
            if A != 'None': x += c['anom'].get(A, 0)
            cap = 70 if (pos == 'PG' and at == 'ID' and A == 'Def') else 99
            pr = max(25, min(cap, math.floor(x + 0.5)))
            if fin >= cap and pr >= cap: continue
            tot += 1
            if pr == fin: hit += 1
            else: off[abs(pr - fin)] = off.get(abs(pr - fin), 0) + 1
print(f"{hit}/{tot} exact ({100*hit/tot:.1f}%); misses by size: {dict(sorted(off.items()))}")
