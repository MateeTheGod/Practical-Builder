"""Joint fit over all positions -> model.json for the calculator.
Per attribute: FINAL = min(cap, round(I_p + h_p*(H-Href_p) + w_p*(WS-H-2) + c_p*(W-Wref_p) + body_b + anom_{p,a}))
Body offsets are shared across positions; everything else is per position, with a cross-position mean as
fallback where a position's data can't identify a coefficient (flagged in the output).
Usage: python -I player-builder-export-model.py OUT.json OBSFILE...
"""
import sys, json, math
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
PG_BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
POS = ["PG", "SG", "SF", "PF", "C"]
HREF = dict(PG=73, SG=77, SF=79, PF=81, C=84)
WREF = dict(PG=180, SG=200, SF=230, PF=260, C=275)
BODIES = ["Slim", "Built", "Narrow", "Bulky"]
ANOMS = ["Fin", "Post", "Def", "Play", "Shoot", "Agility"]
rows, base = [], {}
for fn in sys.argv[2:]:
    pos, b = ("SG" if "-SG" in fn else "PG"), PG_BASE
    for line in open(fn):
        if line.startswith('#POS'): pos = line.split()[1]; continue
        if line.startswith('#BASE'): b = [int(v) for v in line.split()[1:]]; continue
        if line.startswith('#') or not line.strip(): continue
        p = line.split(); base[pos] = b
        rows.append(dict(pos=pos, id=p[0], H=int(p[1]), WS=int(p[2]), W=int(p[3]), A=p[4], B=p[5],
                         d=[int(x) for x in p[6:28]]))
def cap(pos, at, A):
    return 70 if (pos == "PG" and at == "ID" and A == "Def") else 99
# feature layout
cols = []
for p in POS: cols += [("I", p), ("h", p), ("w", p), ("c", p)]
cols += [("body", b) for b in BODIES]
cols += [("anom", p, a) for p in POS for a in ANOMS]
idx = {c: i for i, c in enumerate(cols)}
def feats(r):
    x = [0.0] * len(cols); p = r['pos']
    x[idx[("I", p)]] = 1; x[idx[("h", p)]] = r['H'] - HREF[p]
    x[idx[("w", p)]] = r['WS'] - r['H'] - 2; x[idx[("c", p)]] = r['W'] - WREF[p]
    if r['B'] != 'Normal': x[idx[("body", r['B'])]] = 1
    if r['A'] != 'None': x[idx[("anom", p, r['A'])]] = 1
    return x
def solve(X, y, ridge):
    n = len(X[0])
    A = [[sum(x[i] * x[j] for x in X) + (ridge[i] if i == j else 0) for j in range(n)] for i in range(n)]
    v = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c])); A[c], A[piv] = A[piv], A[c]; v[c], v[piv] = v[piv], v[c]
        if abs(A[c][c]) < 1e-12: continue
        for r in range(n):
            if r != c:
                f = A[r][c] / A[c][c]
                if f: A[r] = [a - f * cc for a, cc in zip(A[r], A[c])]; v[r] -= f * v[c]
    return [v[i] / A[i][i] if abs(A[i][i]) > 1e-12 else 0 for i in range(n)]
seen_anom = {(r['pos'], r['A']) for r in rows}
seen_body = {(r['pos'], r['B']) for r in rows}
model = dict(attrs=ATTR, positions={}, bodies=BODIES, anomalies=ANOMS, bodyOffsets={}, notes={})
tot = good = 0
coef_by_attr = {}
def fit_one(k, at, viol):
    # target is the offset from the position's base row; the intercept is an offset with a mild prior at 0,
    # so when "None" rows are all capped the anomaly terms (not the intercept) take up the difference.
    # viol: censored rows (shown at the cap) that an earlier fit predicted below the cap; they come back
    # with a target just under the cap, so "showed 99" is treated as "at least 99"
    X, y = [], []
    for r in rows:
        fin = base[r['pos']][k] + r['d'][k]
        if fin >= cap(r['pos'], at, r['A']): continue
        X.append(feats(r)); y.append(fin - base[r['pos']][k])
    has = {p: any(x[idx[("I", p)]] == 1 for x in X) for p in POS}  # position has any uncapped value
    for i in sorted(viol):
        r = rows[i]; X.append(feats(r)); y.append(cap(r['pos'], at, r['A']) - 0.3 - base[r['pos']][k])
    ident = [any(abs(x[j]) > 0 for x in X) for j in range(len(cols))]
    for j, c in enumerate(cols):
        if c[0] in ("h", "w", "c") and ident[j]:
            vals = {x[j] for x in X if x[idx[("I", c[1])]] == 1}
            ident[j] = len(vals) > 1
    ridge = [1.0 if c[0] == "I" else 1e-4 for c in cols]
    for j in range(len(cols)):
        if not ident[j]: ridge[j] = 1e6  # pin unidentified to 0, filled below
    coef = solve(X, y, ridge) if X else [0.0] * len(cols)
    est = {}
    # fallbacks (only for positions that have some uncapped data for this attribute;
    # a position whose value was always 99 stays a flat 99)
    for kind in ("h", "w", "c"):
        good_vals = [coef[idx[(kind, p)]] for p in POS if ident[idx[(kind, p)]]]
        m = sum(good_vals) / len(good_vals) if good_vals else 0.0
        for p in POS:
            if not ident[idx[(kind, p)]]:
                coef[idx[(kind, p)]] = m if has[p] else 0.0; est[(kind, p)] = True
    for a in ANOMS:
        good_vals = [coef[idx[("anom", p, a)]] for p in POS if ident[idx[("anom", p, a)]]]
        m = sum(good_vals) / len(good_vals) if good_vals else 0.0
        for p in POS:
            if not ident[idx[("anom", p, a)]]:
                coef[idx[("anom", p, a)]] = m if has[p] else 0.0; est[("anom", p, a)] = True
    # pass 2: hold the fallback values fixed and refit the rest, so intercepts don't absorb them
    fixed = {j: coef[j] for j in range(len(cols)) if not ident[j] and cols[j][0] != "I"}
    if X and fixed:
        y2 = [yy - sum(x[j] * v for j, v in fixed.items()) for x, yy in zip(X, y)]
        coef2 = solve(X, y2, ridge)
        for j, v in fixed.items(): coef2[j] = v
        coef = coef2
    for p in POS:
        if not has[p]: coef[idx[("I", p)]] = 0.0; est[("I", p)] = True
        coef[idx[("I", p)]] += base[p][k]  # back to an absolute intercept
    return coef, est, ident
def pred(r, coef):
    return sum(a * b for a, b in zip(feats(r), coef))
for k, at in enumerate(ATTR):
    coef, est, ident = fit_one(k, at, set())
    # Groups whose every reading sat at the cap only tell us "at least the cap". Raise just that group's
    # own term until its rows reach the cap; no uncapped observation changes.
    for p in POS:
        prow = [r for r in rows if r['pos'] == p]
        for a in ["None"] + ANOMS:
            g = [r for r in prow if r['A'] == a]
            if not g: continue
            capped = [r for r in g if base[p][k] + r['d'][k] >= cap(p, at, a)]
            if len(capped) < len(g): continue          # group has uncapped data: leave the fit alone
            need = max((cap(p, at, a) - 0.49) - pred(r, coef) for r in capped)
            if need <= 0: continue
            if a == "None":
                coef[idx[("I", p)]] += need             # raise the intercept...
                for b in ANOMS:                          # ...and keep anomaly groups that have uncapped data unchanged
                    gb = [r for r in prow if r['A'] == b]
                    if any(base[p][k] + r['d'][k] < cap(p, at, b) for r in gb):
                        coef[idx[("anom", p, b)]] -= need
            else:
                coef[idx[("anom", p, a)]] += need
    coef_by_attr[at] = (coef, est, ident)
    left = [rows[i]['id'] for i, r in enumerate(rows) if base[r['pos']][k] + r['d'][k] >= cap(r['pos'], at, r['A']) and pred(r, coef) < cap(r['pos'], at, r['A']) - 0.5]
    if left: print('  capped rows still predicted low:', at, left)
    # accuracy on observed (uncensored) rows
    for r in rows:
        fin = base[r['pos']][k] + r['d'][k]
        pr = min(cap(r['pos'], at, r['A']), math.floor(sum(a * b for a, b in zip(feats(r), coef)) + 0.5))
        if fin >= cap(r['pos'], at, r['A']):
            continue
        tot += 1; good += (pr == fin)
        if abs(pr - fin) > 1: print('  BIG', r['pos'], r['id'], at, fin, pr)
print(f"joint model: {good}/{tot} uncapped observations reproduced exactly")
for p in POS:
    P = dict(href=HREF[p], wref=WREF[p], base=base[p], coef={}, estimated={},
             seenAnomalies=sorted({a for (q, a) in seen_anom if q == p}),
             seenBodies=sorted({b for (q, b) in seen_body if q == p}),
             heights=sorted({r['H'] for r in rows if r['pos'] == p}),
             weights=sorted({r['W'] for r in rows if r['pos'] == p}))
    for at in ATTR:
        coef, est, ident = coef_by_attr[at]
        P['coef'][at] = dict(I=round(coef[idx[("I", p)]], 4), h=round(coef[idx[("h", p)]], 4),
                             w=round(coef[idx[("w", p)]], 4), c=round(coef[idx[("c", p)]], 4),
                             anom={a: round(coef[idx[("anom", p, a)]], 4) for a in ANOMS})
        P['estimated'][at] = sorted(k[0] if k[0] != "anom" else "anom:" + k[2] for k in est if k[1] == p)
    model['positions'][p] = P
for at in ATTR:
    coef, est, ident = coef_by_attr[at]
    model['bodyOffsets'][at] = {b: round(coef[idx[("body", b)]], 4) for b in BODIES}
json.dump(model, open(sys.argv[1], "w"), indent=1)
print("wrote", sys.argv[1])

