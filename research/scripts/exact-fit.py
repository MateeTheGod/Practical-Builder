"""Look for coefficients that reproduce EVERY observation exactly (interval constraints instead of least squares).
For each position and attribute: find theta with  fin-0.5 <= x.theta <= fin+0.5-eps  for uncapped rows and
x.theta >= cap-0.5 for capped rows. Solved by cyclic projections (Agmon-Motzkin relaxation) starting from the
least-squares answer; reports feasible / the rows that stay violated.
Usage: python -I player-builder-exact-fit.py OUT.json OBSFILES...
"""
import sys, json, math
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
PG_BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
HREF = dict(PG=73, SG=77, SF=79, PF=81, C=84); WREF = dict(PG=180, SG=200, SF=230, PF=260, C=275)
rows, base = [], {}
for fn in sys.argv[2:]:
    pos, b = ("SG" if "-SG" in fn else "PG"), PG_BASE
    for line in open(fn, encoding="utf-8-sig"):
        if line.startswith('#POS'): pos = line.split()[1]; continue
        if line.startswith('#BASE'): b = [int(v) for v in line.split()[1:]]; continue
        if line.startswith('#') or not line.strip(): continue
        p = line.split(); base[pos] = b
        rows.append(dict(pos=pos, id=p[0], H=int(p[1]), WS=int(p[2]), W=int(p[3]), A=p[4], B=p[5], d=[int(x) for x in p[6:28]]))
def cap(pos, at, A): return 70 if (pos == "PG" and at == "ID" and A == "Def") else 99
import os
HOLD = []
if os.environ.get("HOLDOUT"):  # e.g. HOLDOUT=T -> rows whose id starts with T are left out of the fit
    HOLD = [r for r in rows if r['id'].startswith(os.environ["HOLDOUT"])]
    rows = [r for r in rows if not r['id'].startswith(os.environ["HOLDOUT"])]
EPS = 1e-3
result = {}
for pos in ["PG", "SG", "SF", "PF", "C"]:
    R = [r for r in rows if r['pos'] == pos]
    bodies = sorted({r['B'] for r in R} - {"Normal"}); anoms = sorted({r['A'] for r in R} - {"None"})
    names = ["1", "h", "w", "c10"] + bodies + anoms
    def feats(r):
        return [1.0, r['H'] - HREF[pos], r['WS'] - r['H'] - 2, (r['W'] - WREF[pos]) / 10] + \
               [float(r['B'] == b) for b in bodies] + [float(r['A'] == a) for a in anoms]
    result[pos] = {}
    for k, at in enumerate(ATTR):
        cons = []  # (x, lo, hi, id)
        for r in R:
            fin = base[pos][k] + r['d'][k]; cp = cap(pos, at, r['A']); x = feats(r)
            if fin >= cp: cons.append((x, cp - 0.5, 1e9, r['id']))
            else: cons.append((x, fin - 0.5, fin + 0.5 - EPS, r['id']))
        unc = [c for c in cons if c[2] < 1e8]
        if len(unc) < 2:
            result[pos][at] = dict(status="always capped"); continue
        n = len(names)
        active = [any(abs(c[0][j]) > 0 for c in cons) for j in range(n)]
        def relax(m, th):
            # shrink every uncapped interval by margin m (prefer solutions far from rounding edges)
            for sweep in range(2500):
                worst = 0.0
                for x, lo, hi, _ in cons:
                    lo2, hi2 = (lo + m, hi - m) if hi < 1e8 else (lo + m, hi)
                    v = sum(a * b for a, b in zip(x, th))
                    tgt = lo2 + 1e-4 if v < lo2 else (hi2 - 1e-4 if v > hi2 else None)
                    if tgt is None: continue
                    worst = max(worst, abs(v - tgt))
                    nn = sum(a * a for a, j in zip(x, range(n)) if active[j])
                    step = (tgt - v) / nn
                    th = [t + (step * a if active[j] else 0) for j, (t, a) in enumerate(zip(th, x))]
                if worst < 1e-9: return th, True
            return th, False
        th0 = [0.0] * n; th0[0] = sum(c[1] + 0.5 for c in unc) / len(unc)
        if os.environ.get("FROM_LS"):
            # start at the least-squares answer and move only as far as needed (projections from there)
            Xu = [c[0] for c in unc]; yu = [c[1] + 0.5 for c in unc]
            A = [[sum(x[i] * x[j] for x in Xu) + (1e-6 if i == j else 0) for j in range(n)] for i in range(n)]
            v = [sum(x[i] * yy for x, yy in zip(Xu, yu)) for i in range(n)]
            for c_ in range(n):
                piv = max(range(c_, n), key=lambda r_: abs(A[r_][c_])); A[c_], A[piv] = A[piv], A[c_]; v[c_], v[piv] = v[piv], v[c_]
                for r_ in range(n):
                    if r_ != c_ and A[c_][c_]:
                        f = A[r_][c_] / A[c_][c_]; A[r_] = [a - f * cc for a, cc in zip(A[r_], A[c_])]; v[r_] -= f * v[c_]
            th0 = [v[i] / A[i][i] if A[i][i] else 0 for i in range(n)]
        th, margin = th0, None
        for m in ((0.0,) if os.environ.get("FROM_LS") else (0.4, 0.3, 0.2, 0.12, 0.06, 0.02, 0.0)):
            t, ok = relax(m, list(th))
            if ok: th, margin = t, m; break
        if margin is None: th = t
        viol = []
        for x, lo, hi, rid in cons:
            v = sum(a * b for a, b in zip(x, th))
            if v < lo - 1e-6 or v > hi + 1e-6: viol.append((rid, round(v, 2), lo + 0.5 if hi < 1e8 else "cap"))
        # held-out rows: predict them with this fit
        ho = []
        for r in HOLD:
            if r['pos'] != pos: continue
            v = sum(a * b for a, b in zip(feats(r), th)); fin = base[pos][k] + r['d'][k]; cp = cap(pos, at, r['A'])
            pr = min(cp, math.floor(v + 0.5))
            ho.append((r['id'], fin, pr))
        result[pos][at] = dict(status="exact" if not viol else "conflict", margin=margin,
                               coef=dict(zip(names, [round(t, 4) for t in th])), violations=viol, holdout=ho)
    ok = sum(1 for v in result[pos].values() if v['status'] == "exact")
    bad = {a: v['violations'] for a, v in result[pos].items() if v['status'] == "conflict"}
    print(f"{pos}: {ok} attributes fit every observation exactly; conflicts: " + (json.dumps(bad) if bad else "none"))
if HOLD:
    tot = hit = 0
    for pos in result:
        for at, v in result[pos].items():
            for rid, fin, pr in v.get('holdout', []):
                if fin >= 99 and pr >= 99: continue
                tot += 1; hit += (fin == pr)
                if fin != pr: print("  held-out miss", pos, rid, at, "shown", fin, "predicted", pr)
    print(f"held-out: {hit}/{tot} exact")
json.dump(result, open(sys.argv[1], "w"), indent=1)
