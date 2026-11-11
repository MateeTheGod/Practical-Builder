"""Fit FINAL = min(99, round(c0 + a*(H-Href) + b*(WS-H) + c*(W-Wref) + body + anomaly)) per position block.
Usage: python -I player-builder-fit-multi.py FILE [FILE...]   (files with '#POS name' / '#BASE ...' headers,
or a single-position file with only '#BASE' or the PG default)."""
import sys, math
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
PG_BASE = [84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99]
blocks = {}
for fn in sys.argv[1:]:
    pos, base = fn.split('-')[-1].split('.')[0] if '-SG' in fn else 'PG', PG_BASE
    if '-SG' in fn: pos = 'SG'
    for line in open(fn):
        if line.startswith('#POS'):
            pos = line.split()[1]; continue
        if line.startswith('#BASE'):
            base = [int(v) for v in line.split()[1:]]; continue
        if line.startswith('#') or not line.strip():
            continue
        p = line.split()
        b = blocks.setdefault(pos, dict(base=base, rows=[]))
        b['base'] = base
        b['rows'].append(dict(id=p[0], H=int(p[1]), WS=int(p[2]), W=int(p[3]), A=p[4], B=p[5], d=[int(x) for x in p[6:28]]))
def solve(X, y, lam=1e-6):
    n = len(X[0])
    A = [[sum(x[i] * x[j] for x in X) + (lam if i == j else 0) for j in range(n)] for i in range(n)]
    v = [sum(x[i] * yy for x, yy in zip(X, y)) for i in range(n)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c])); A[c], A[piv] = A[piv], A[c]; v[c], v[piv] = v[piv], v[c]
        for r in range(n):
            if r != c and A[c][c]:
                f = A[r][c] / A[c][c]; A[r] = [a - f * cc for a, cc in zip(A[r], A[c])]; v[r] -= f * v[c]
    return [v[i] / A[i][i] if A[i][i] else 0 for i in range(n)]
for pos, blk in blocks.items():
    rows, BASE = blk['rows'], blk['base']
    bodies = sorted({r['B'] for r in rows} - {'Normal'}); anoms = sorted({r['A'] for r in rows} - {'None'})
    H0 = min(r['H'] for r in rows); W0 = min(r['W'] for r in rows)
    names = ['1', f'H-{H0}', 'WS-H', f'W-{W0}'] + bodies + anoms
    def feats(r):
        return [1.0, r['H'] - H0, r['WS'] - r['H'], r['W'] - W0] + [float(r['B'] == b) for b in bodies] + [float(r['A'] == a) for a in anoms]
    print(f"\n===== {pos}: {len(rows)} states; features {names}")
    tot = miss_tot = 0
    for k, at in enumerate(ATTR):
        X, y = [], []
        for r in rows:
            fin = BASE[k] + r['d'][k]
            if fin >= 99: continue
            X.append(feats(r)); y.append(fin)
        if len(X) < 4:
            print(f"{at}: capped/too few ({len(X)})"); continue
        c = solve(X, y)
        miss = []
        for r in rows:
            fin = BASE[k] + r['d'][k]
            pr = min(99, math.floor(sum(a * b for a, b in zip(feats(r), c)) + 0.5))
            if fin >= 99 and pr >= 99: continue
            if fin >= 99 and pr < 99:
                # censored row: only a miss if the model is clearly below the cap
                if pr < 98: miss.append((r['id'], '99', pr))
                continue
            tot += 1
            if pr != fin: miss.append((r['id'], fin, pr))
        miss_tot += len([m for m in miss if m[1] != '99'])
        coefs = " ".join(f"{n}={v:+.2f}" for n, v in zip(names, c) if n != '1')
        print(f"{at}: n={len(X)} {coefs}" + (f"\n    misses {miss}" if miss else ""))
    print(f"--- {pos}: {tot - miss_tot}/{tot} uncapped values reproduced exactly")
