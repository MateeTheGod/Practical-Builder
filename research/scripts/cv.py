"""Compare model structures by 5-fold cross-validation (exact-match rate on held-out uncapped values).
Variants: linear | +HxW etc. interactions | +anomaly x inputs | +body x inputs | all.
Usage: python -I player-builder-cv.py OBSFILE..."""
import sys, math, random
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
PG_BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
HREF = dict(PG=73, SG=77, SF=79, PF=81, C=84); WREF = dict(PG=180, SG=200, SF=230, PF=260, C=275)
rows = []
for fn in sys.argv[1:]:
    pos, base = ("SG" if "-SG" in fn else "PG"), PG_BASE
    for line in open(fn, encoding="utf-8-sig"):
        if line.startswith('#POS'): pos = line.split()[1]; continue
        if line.startswith('#BASE'): base = [int(v) for v in line.split()[1:]]; continue
        if line.startswith('#') or not line.strip(): continue
        q = line.split()
        rows.append(dict(pos=pos, H=int(q[1]), WS=int(q[2]), W=int(q[3]), A=q[4], B=q[5], fin=[b + int(x) for b, x in zip(base, q[6:28])]))
def solve(X, y, lam=1e-3):
    n = len(X[0])
    A = [[sum(x[i] * x[j] for x in X) + (lam if i == j else 0) for j in range(n)] for i in range(n)]
    v = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c])); A[c], A[piv] = A[piv], A[c]; v[c], v[piv] = v[piv], v[c]
        if abs(A[c][c]) < 1e-12: continue
        for r in range(n):
            if r != c:
                f = A[r][c] / A[c][c]
                if f: A[r] = [a - f * cc for a, cc in zip(A[r], A[c])]; v[r] -= f * v[c]
    return [v[i] / A[i][i] if abs(A[i][i]) > 1e-12 else 0 for i in range(n)]
def make_feats(variant, bodies, anoms, pos):
    def f(r):
        h = r['H'] - HREF[pos]; s = r['WS'] - r['H'] - 2; w = (r['W'] - WREF[pos]) / 10
        x = [1.0, h, s, w]
        bd = [float(r['B'] == b) for b in bodies]; an = [float(r['A'] == a) for a in anoms]
        x += bd + an
        if variant in ("inter", "all"): x += [h * w, s * w, h * s, h * h, w * w, s * s]
        if variant in ("anomx", "all"):
            for a in an: x += [a * h, a * s, a * w]
        if variant in ("bodyx", "all"):
            for b in bd: x += [b * h, b * w]
        return x
    return f
def cv(variant, folds=5, seed=1):
    random.seed(seed); idx = list(range(len(rows))); random.shuffle(idx)
    fold_of = {i: k % folds for k, i in enumerate(idx)}
    tot = hit = 0
    for pos in HREF:
        R = [i for i in range(len(rows)) if rows[i]['pos'] == pos]
        bodies = sorted({rows[i]['B'] for i in R} - {"Normal"}); anoms = sorted({rows[i]['A'] for i in R} - {"None"})
        feats = make_feats(variant, bodies, anoms, pos)
        for k, at in enumerate(ATTR):
            cap = lambda r: 70 if (pos == "PG" and at == "ID" and r['A'] == "Def") else 99
            for fo in range(folds):
                tr = [rows[i] for i in R if fold_of[i] != fo and rows[i]['fin'][k] < cap(rows[i])]
                te = [rows[i] for i in R if fold_of[i] == fo]
                if len(tr) < 8: continue
                c = solve([feats(r) for r in tr], [r['fin'][k] for r in tr])
                for r in te:
                    fin = r['fin'][k]; pr = min(cap(r), math.floor(sum(a * b for a, b in zip(feats(r), c)) + 0.5))
                    if fin >= cap(r) and pr >= cap(r): continue
                    if fin >= cap(r): continue
                    tot += 1; hit += (pr == fin)
    return hit, tot
for v in ("linear", "inter", "anomx", "bodyx", "all"):
    h, t = cv(v); print(f"{v:7s}: {h}/{t} held-out exact ({100*h/t:.1f}%)")
