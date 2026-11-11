"""For every one-setting-at-a-time sweep (weight / height / wingspan, per position, per attribute),
test whether ANY straight line round(a + b*x) reproduces every displayed value exactly.
If not, test a quadratic and a two-piece line (kink). Prints which sweeps need curvature.
Usage: python -I player-builder-curve-test.py SWEEPFILE"""
import sys
ATTR = "CS DL DD SD MR TP MS FT PA BH PC ID PD LS ST BL RB SP AC STR VE STA".split()
HREF = dict(PG=73, SG=77, SF=79, PF=81, C=84); WREF = dict(PG=180, SG=200, SF=230, PF=260, C=275)
rows = []
for line in open(sys.argv[1], encoding="utf-8-sig"):
    if line.startswith('#') or not line.strip(): continue
    q = line.split()
    rows.append(dict(pos=q[1], H=int(q[2]), WS=int(q[3]), W=int(q[4]), A=q[5], B=q[6], v=[int(x) for x in q[7:29]]))

def series(pos, kind):
    out = {}
    for r in rows:
        if r['pos'] != pos or r['A'] != 'None' or r['B'] != 'Normal': continue
        h0, w0 = HREF[pos], WREF[pos]
        if kind == 'W' and r['H'] == h0 and r['WS'] == h0 + 2: out[r['W']] = r['v']
        if kind == 'H' and r['WS'] == r['H'] + 2 and r['W'] == w0: out[r['H']] = r['v']
        if kind == 'S' and r['H'] == h0 and r['W'] == w0: out[r['WS'] - h0] = r['v']
    return sorted(out.items())

def feasible(pts, basis, grids):
    """pts: [(x,y)]. basis: list of functions of x (first is the free intercept, solved as an interval).
    grids: list of candidate values for the other coefficients. Returns a solution or None."""
    def rec(i, coefs):
        if i == len(grids):
            lo = max(y - 0.5 - sum(c * f(x) for c, f in zip(coefs, basis[1:])) for x, y in pts)
            hi = min(y + 0.5 - sum(c * f(x) for c, f in zip(coefs, basis[1:])) for x, y in pts)
            return [(lo + hi) / 2] + coefs if lo < hi - 1e-9 else None
        for g in grids[i]:
            s = rec(i + 1, coefs + [g])
            if s: return s
        return None
    return rec(0, [])

def frange(a, b, n): return [a + (b - a) * k / n for k in range(n + 1)]
total = lin_ok = 0; bad = []
for pos in HREF:
    for kind in "WHS":
        S = series(pos, kind)
        if len(S) < 4: continue
        for k, at in enumerate(ATTR):
            cap = 70 if (pos == "PG" and at == "ID") else 99
            pts = [((x - (WREF[pos] if kind == 'W' else HREF[pos] if kind == 'H' else 2)) / (10 if kind == 'W' else 1), v[k]) for x, v in S]
            pts = [(x, y) for x, y in pts if y < 99]
            if len(pts) < 4 or len({y for _, y in pts}) == 1: continue
            total += 1
            ys = [y for _, y in pts]; xs = [x for x, _ in pts]
            span = (max(ys) - min(ys) + 1) / max(1e-9, (max(xs) - min(xs)))
            lin = feasible(pts, [lambda x: 1, lambda x: x], [frange(-span * 1.5, span * 1.5, 3000)])
            if lin: lin_ok += 1; continue
            quad = feasible(pts, [lambda x: 1, lambda x: x, lambda x: x * x],
                            [frange(-span * 1.5, span * 1.5, 300), frange(-0.6, 0.6, 240)])
            kink = None
            for x0 in sorted(set(xs))[1:-1]:
                kink = feasible(pts, [lambda x: 1, lambda x: min(x, x0), lambda x: max(x - x0, 0)],
                                [frange(-span * 2, span * 2, 300), frange(-span * 2, span * 2, 300)])
                if kink: kink = (x0, kink); break
            bad.append((pos, kind, at, pts, quad, kink))
print(f"sweeps tested: {total}; exactly fit by a straight line: {lin_ok}; need something else: {len(bad)}")
for pos, kind, at, pts, quad, kink in bad:
    q = "quad OK c=%.3f" % quad[2] if quad else "quad NO"
    kk = "kink at %g OK slopes %.2f/%.2f" % (kink[0], kink[1][1], kink[1][2]) if kink else "kink NO"
    print(f"{pos} {kind} {at:3s} | {q:16s} | {kk:30s} | " + " ".join(f"{x:g}:{y}" for x, y in pts))
