"""Snap the least-squares model onto the live sweeps: for every position/attribute, keep the
intercept, slopes, body and anomaly offsets inside the ranges where the one-setting sweeps are
reproduced exactly, choosing the value closest to the least-squares one (mode=clamp) or the middle
of the range (mode=mid). Writes a model.json in the same format.
Usage: python -I player-builder-sweep-snap.py SWEEPFILE LSMODEL.json OUT.json [clamp|mid]"""
import sys, json, copy
sweepf, lsf, outf = sys.argv[1:4]; mode = sys.argv[4] if len(sys.argv) > 4 else "clamp"
m = json.load(open(lsf)); out = copy.deepcopy(m); ATTR = m['attrs']
HREF = dict(PG=73, SG=77, SF=79, PF=81, C=84); WREF = dict(PG=180, SG=200, SF=230, PF=260, C=275)
rows = []
for line in open(sweepf, encoding="utf-8-sig"):
    if line.startswith('#') or not line.strip(): continue
    q = line.split()
    rows.append(dict(pos=q[1], H=int(q[2]), WS=int(q[3]), W=int(q[4]), A=q[5], B=q[6], v=[int(x) for x in q[7:29]]))
BASES = dict(PG=[84,87,70,45,91,91,92,99,99,94,59,52,80,91,99,55,52,95,94,65,91,99],
             SG=[85,87,75,55,96,96,96,99,88,83,63,61,87,80,81,62,65,90,90,73,88,99],
             SF=[95,97,95,79,88,83,81,99,84,77,75,88,95,79,77,84,85,85,84,81,96,99],
             PF=[97,99,97,87,83,82,74,99,92,72,86,91,88,77,72,87,99,81,80,85,88,99],
             C=[99,97,88,99,82,81,71,99,91,61,99,95,82,71,66,96,99,69,69,95,71,99])
for p, b in BASES.items():
    rows.append(dict(pos=p, H=HREF[p], WS=HREF[p] + 2, W=WREF[p], A='None', B='Normal', v=b))
INF = 1e9
def bounds(y, cap): return (y - 0.5, INF) if y >= cap else (y - 0.5, y + 0.5)
def clamp(v, lo, hi, mid):
    if mode == "mid": return mid
    return min(max(v, lo + 1e-6), hi - 1e-6)
stats = dict(attrs=0, snapped=0, infeasible=0)
for pos in HREF:
    h0, w0 = HREF[pos], WREF[pos]
    R = [r for r in rows if r['pos'] == pos]
    P = out['positions'][pos]; P.setdefault('body', {})
    for k, at in enumerate(ATTR):
        c = P['coef'][at]; stats['attrs'] += 1
        cap = 99
        axes = {'h': [], 'w': [], 'c': []}; base = None; offs = []
        for r in R:
            nb = r['A'] == 'None' and r['B'] == 'Normal'
            dh, ds, dw = r['H'] - h0, r['WS'] - r['H'] - 2, r['W'] - w0
            lo, hi = bounds(r['v'][k], cap)
            if nb and dh == 0 and ds == 0 and dw == 0: base = (lo, hi)
            elif nb and dh == 0 and ds == 0: axes['c'].append((dw, lo, hi))
            elif nb and ds == 0 and dw == 0: axes['h'].append((dh, lo, hi))
            elif nb and dh == 0 and dw == 0: axes['w'].append((ds, lo, hi))
            elif dh == 0 and ds == 0 and dw == 0 and (r['A'] == 'None') != (r['B'] == 'Normal'):
                offs.append((r['A'] if r['A'] != 'None' else r['B'], r['A'] != 'None', lo, hi))
        if base is None: continue
        def slope_iv(a, pts):
            lo, hi = -INF, INF
            for x, ylo, yhi in pts:
                l, u = (ylo - a) / x, (yhi - a) / x
                if x < 0: l, u = u, l
                lo, hi = max(lo, l), min(hi, u)
            return lo, hi
        alo, ahi = base[0], min(base[1], base[0] + 20)
        grid = [alo + (ahi - alo) * (i + 0.5) / 400 for i in range(400)]
        ok = [a for a in grid if all(slope_iv(a, p)[0] < slope_iv(a, p)[1] for p in axes.values())]
        if not ok: stats['infeasible'] += 1; continue
        stats['snapped'] += 1
        a = min(ok, key=lambda g: abs(g - c['I'])) if mode == "clamp" else ok[len(ok) // 2]
        c['I'] = a
        scale = {'h': 1, 'w': 1, 'c': 1}
        for key, pts in axes.items():
            lo, hi = slope_iv(a, pts)
            if lo == -INF and hi == INF: continue
            mid = (lo + hi) / 2 if hi < INF and lo > -INF else (lo + 0.5 if lo > -INF else hi - 0.5)
            c[key] = clamp(c[key], lo, hi, mid)
        for name, is_anom, lo, hi in offs:
            lo -= a; hi -= a
            cur = c['anom'].get(name, 0) if is_anom else (P['body'].get(at, {}) or {}).get(name, m['bodyOffsets'][at].get(name, 0))
            mid = (lo + hi) / 2 if hi < INF / 2 else max(cur, lo + 0.5)
            v = clamp(cur, lo, hi if hi < INF / 2 else INF, mid)
            if is_anom: c['anom'][name] = v
            else: P['body'].setdefault(at, {})[name] = v
for pos in HREF:
    P = out['positions'][pos]
    for at in ATTR:  # positions without a sweep entry keep the shared offsets
        P['body'].setdefault(at, dict(m['bodyOffsets'][at]))
        for b, v in m['bodyOffsets'][at].items(): P['body'][at].setdefault(b, v)
json.dump(out, open(outf, "w"), indent=1)
print(mode, stats)
