import sys, math
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
rows = []
IDCAP = int(sys.argv[2]) if len(sys.argv) > 2 else 70
for line in open(sys.argv[1]):
    if line.startswith('#BASE'):
        BASE = [int(v) for v in line.split()[1:]]
        continue
    if line.startswith('#') or not line.strip():
        continue
    p = line.split()
    rows.append(dict(id=p[0], H=int(p[1]), WS=int(p[2]), W=int(p[3]), A=p[4], B=p[5],
                     d=[int(x) for x in p[6:28]]))
FEAT = ["1", "H-72", "WS-H", "W-190", "Slim", "Built", "Narrow", "Fin", "Post", "Def"]
def feats(r):
    return [1, r['H'] - 72, r['WS'] - r['H'], r['W'] - 190,
            r['B'] == 'Slim', r['B'] == 'Built', r['B'] == 'Narrow',
            r['A'] == 'Fin', r['A'] == 'Post', r['A'] == 'Def']
def solve(X, y, lam=1e-6):
    n = len(X[0])
    A = [[sum(x[i] * x[j] for x in X) + (lam if i == j else 0) for j in range(n)] for i in range(n)]
    b = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c]))
        A[c], A[piv] = A[piv], A[c]; b[c], b[piv] = b[piv], b[c]
        for r in range(n):
            if r != c and A[c][c] != 0:
                f = A[r][c] / A[c][c]
                A[r] = [a - f * cc for a, cc in zip(A[r], A[c])]; b[r] -= f * b[c]
    return [b[i] / A[i][i] if A[i][i] else 0 for i in range(n)]
for k, name in enumerate(ATTR):
    X, y, ids = [], [], []
    for r in rows:
        fin = BASE[k] + r['d'][k]
        if fin >= 99 or (name == 'ID' and r['A'] == 'Def' and fin >= IDCAP):  # censored by 99 cap (ID under Def looks capped at 70)
            continue
        X.append([float(v) for v in feats(r)]); y.append(BASE[k] + r['d'][k]); ids.append(r['id'])
    if len(X) < 3:
        print(f"{name}: always capped at 99 ({len(X)} uncensored)"); continue
    c = solve(X, y)
    res = [(i, yy, sum(a * b for a, b in zip(x, c))) for i, x, yy in zip(ids, X, y)]
    bad = [(i, yy, round(p, 2)) for i, yy, p in res if abs(p - yy) > 0.5]
    mx = max(abs(p - yy) for _, yy, p in res)
    print(f"{name}: n={len(X)} maxerr={mx:.2f} " + " ".join(f"{f}={v:+.3f}" for f, v in zip(FEAT, c)))
    if bad:
        print("   off>0.5:", bad)

    # exact-match check on ALL rows using coefficients rounded to 3 dp, Final = min(cap, round(pred))
    c3 = [round(v, 3) for v in c]
    miss = []
    for r in rows:
        p = sum(a * b for a, b in zip([float(v) for v in feats(r)], c3))
        cap = IDCAP if (name == 'ID' and r['A'] == 'Def') else 99
        pr = min(99, cap, math.floor(p + 0.5))
        ob = BASE[k] + r['d'][k]
        if pr != ob:
            miss.append((r['id'], ob, pr))
    print(f"   exact matches {len(rows)-len(miss)}/{len(rows)}", miss if miss else "")


