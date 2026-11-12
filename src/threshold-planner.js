// Exact threshold planning. Rating totals are an objective, never game costs or OVR.
const ThresholdPlanner = (() => {
  function alternatives(rule, mode) {
    let out = [{}];
    for (const [key, value] of rule) {
      const keys = key !== 'DUNK' ? [key] : mode === 'max' ? ['DD', 'SD'] : [mode];
      out = out.flatMap(v => keys.map(k => ({ ...v, [k]: Math.max(v[k] || 25, value) })));
    }
    return out;
  }

  function solve({ attrs, caps, badges, targets = {}, floors = {}, dunkMode = 'DD' }) {
    if (!['DD', 'SD', 'max'].includes(dunkMode)) throw new Error('Invalid dunk interpretation');
    const base = Object.fromEntries(attrs.map(k => [k, floors[k] === undefined ? 25 : floors[k]]));
    const errors = [];
    for (const k of attrs) {
      if (!Number.isInteger(caps[k]) || caps[k] < 25 || caps[k] > 99) throw new Error('Invalid cap: ' + k);
      if (!Number.isInteger(base[k]) || base[k] < 25 || base[k] > 99) throw new Error('Invalid minimum: ' + k);
      if (base[k] > caps[k]) errors.push({ type: 'floor', attr: k, needed: base[k], cap: caps[k] });
    }
    const fits = v => Object.entries(v).every(([k, n]) => attrs.includes(k) && n <= caps[k]);
    const constraints = [];
    // Include earlier tiers too, matching the calculator's tierOf() prefix semantics.
    for (const [name, tier] of Object.entries(targets)) {
      if (!tier) continue;
      const badge = badges.find(b => b.name === name);
      if (!badge || !Number.isInteger(tier) || tier < 1 || tier > badge.tiers.length) throw new Error('Invalid badge target: ' + name);
      for (let i = 0; i < tier; i++) {
        const paths = badge.tiers[i].flatMap(rule => alternatives(rule, dunkMode));
        const options = paths.filter(fits);
        if (!options.length) {
          errors.push({ type: 'badge', name, tier: i + 1, paths });
          break;
        }
        constraints.push({ name, options });
      }
    }
    if (errors.length) return { ok: false, errors };

    const cost = v => attrs.reduce((sum, k) => sum + v[k] - 25, 0);
    const dominates = (a, b) => attrs.every(k => a[k] <= b[k]);
    let frontier = [base];
    // Combining alternatives jointly avoids the greedy error of paying twice for shared stats.
    for (const { options } of constraints.sort((a, b) => a.options.length - b.options.length)) {
      const seen = new Map();
      for (const v of frontier) for (const option of options) {
        const merged = { ...v };
        for (const [k, n] of Object.entries(option)) merged[k] = Math.max(merged[k], n);
        seen.set(attrs.map(k => merged[k]).join(','), merged);
      }
      const next = [];
      for (const v of [...seen.values()].sort((a, b) => cost(a) - cost(b))) {
        if (!next.some(other => dominates(other, v))) next.push(v);
      }
      frontier = next;
    }
    const ratings = frontier.reduce((best, v) => cost(v) < cost(best) ? v : best);
    const support = Object.fromEntries(attrs.map(k => [k, []]));
    for (const { name, options } of constraints) {
      const path = options.find(option => Object.entries(option).every(([k, n]) => ratings[k] >= n));
      for (const [k, n] of Object.entries(path)) {
        if (n === ratings[k] && !support[k].includes(name)) support[k].push(name);
      }
    }
    return { ok: true, ratings, support, ratingIncreases: cost(ratings) };
  }
  return { solve };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = ThresholdPlanner;
