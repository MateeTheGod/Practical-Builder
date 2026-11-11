"""Predict FINAL values for test builds using the model fitted in player-builder-fit.py.
Usage: python -I player-builder-predict.py player-builder-observations.txt
Marks: * = would exceed 99 (shows 99), ? = within 0.15 of a .5 rounding edge (could be +/-1),
       c = cap-affected / unidentifiable coefficient (prediction not meaningful).
"""
import sys, math
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
rows = []
for line in open(sys.argv[1]):
    if line.startswith('#') or not line.strip():
        continue
    p = line.split()
    rows.append(dict(id=p[0], H=int(p[1]), WS=int(p[2]), W=int(p[3]), A=p[4], B=p[5], d=[int(x) for x in p[6:28]]))
def feats(r):
    return [1, r['H'] - 72, r['WS'] - r['H'], r['W'] - 190, r['B'] == 'Slim', r['B'] == 'Built', r['B'] == 'Narrow',
            r['A'] == 'Fin', r['A'] == 'Post', r['A'] == 'Def']
def solve(X, y, lam=1e-6):
    n = len(X[0])
    A = [[sum(x[i] * x[j] for x in X) + (lam if i == j else 0) for j in range(n)] for i in range(n)]
    b = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c])); A[c], A[piv] = A[piv], A[c]; b[c], b[piv] = b[piv], b[c]
        for r in range(n):
            if r != c and A[c][c]:
                f = A[r][c] / A[c][c]; A[r] = [a - f * cc for a, cc in zip(A[r], A[c])]; b[r] -= f * b[c]
    return [b[i] / A[i][i] if A[i][i] else 0 for i in range(n)]
coef, ident = {}, {}
for k, name in enumerate(ATTR):
    X, y = [], []
    for r in rows:
        fin = BASE[k] + r['d'][k]
        if fin >= 99 or (name == 'ID' and r['A'] == 'Def' and fin >= 70):
            continue
        X.append([float(v) for v in feats(r)]); y.append(fin)
    if len(X) < 10:
        coef[name] = None; continue
    coef[name] = solve(X, y)
    # which dummies were ever observed uncensored
    ident[name] = [any(x[j] for x in X) for j in range(10)]
def ft(s):
    f, i = s.split("'"); return int(f) * 12 + int(i)
BUILDS = [line.split('|') for line in """\
T1 interpolation (all inputs inside seen range)|6'2|6'4|180|None|Normal
T2 extrapolate up (taller/longer/heavier)|6'6|6'10|205|None|Normal
T3 extrapolate down (light)|5'9|5'9|150|None|Normal
T4 Slim offsets on an uncapped build|6'4|6'6|205|None|Slim
T5 Narrow offsets on an uncapped build|6'4|6'6|205|None|Narrow
T6 Built offsets on an uncapped build|6'4|6'6|205|None|Built
T7 ID cap under Defense (no-cap ID would be well above 70)|6'4|6'9|205|Def|Built
T8 Defense, short/light (ID should drop below 70 if NOT a cap)|5'9|5'9|160|Def|Slim
T9 Post-Scoring + Narrow (anomaly+body additivity)|6'3|6'7|205|Post|Narrow
T10 Finishing, heavy & tall (uncaps Vertical/Speed?)|6'5|6'9|205|Fin|Built
T11 tall, minimum wingspan, light|6'6|6'6|160|None|Normal
T12 Post-Scoring vs T1 (same body; differences should be +5,+5,0,0,+9,-11,-5,..)|6'2|6'4|180|Post|Normal""".splitlines()]
for name, h, ws, w, a, b in BUILDS:
    r = dict(H=ft(h), WS=ft(ws), W=int(w), A=a, B=b)
    x = [float(v) for v in feats(r)]
    out = []
    for k, at in enumerate(ATTR):
        c = coef[at]
        if c is None or (at == 'PA' and a == 'None'):
            out.append(f"{at}=99c"); continue
        used = [j for j in range(4, 10) if x[j]]
        unk = any(not ident[at][j] for j in used)
        p = sum(u * v for u, v in zip(x, c))
        if at == 'ID' and a == 'Def':
            out.append(f"ID={min(70, math.floor(p + 0.5))}"); continue
        v = math.floor(p + 0.5)
        mark = ('c' if unk else '') + ('*' if v >= 99 else '') + ('?' if abs((p % 1) - 0.5) < 0.15 else '')
        out.append(f"{at}={min(99, v)}{mark}")
    print(f"{name}: {h} / WS {ws} / {w} lb / {a} / {b}\n   " + "  ".join(out))



