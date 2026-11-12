// Exact minimum planning plus a bounded badge improvement search under a partial cost rule.
const ThresholdPlanner = (() => {
  // User-reported working rule. 89->90 is the first priced step; lower ratings are unpriced.
  const COST_RULE = Object.freeze({ firstRating: 90, perStep: 3, ceiling: 99, status: 'user-reported' });
  const knownCost = ratings => Object.values(ratings).reduce((sum, n) => sum + Math.max(0, n - COST_RULE.firstRating + 1) * COST_RULE.perStep, 0);
  function alternatives(rule, mode) {
    let out = [{}];
    for (const [key, value] of rule) {
      const keys = key !== 'DUNK' ? [key] : mode === 'max' ? ['DD', 'SD'] : [mode];
      out = out.flatMap(v => keys.map(k => ({ ...v, [k]: Math.max(v[k] || 25, value) })));
    }
    return out;
  }

  function solve({ attrs, caps, badges, targets = {}, floors = {}, dunkMode = 'DD', knownBudget = null }) {
    if (knownBudget !== null && (!Number.isFinite(knownBudget) || knownBudget < 0)) throw new Error('Invalid known-cost ceiling');
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
    if (knownBudget !== null) {
      const minimum = Math.min(...frontier.map(knownCost));
      frontier = frontier.filter(v => knownCost(v) <= knownBudget);
      if (!frontier.length) return { ok: false, errors: [{ type: 'budget', needed: minimum, ceiling: knownBudget }] };
    }
    const compare = (a, b) => (knownBudget === null ? 0 : knownCost(a) - knownCost(b)) || cost(a) - cost(b);
    const ratings = frontier.reduce((best, v) => compare(v, best) < 0 ? v : best);
    const support = Object.fromEntries(attrs.map(k => [k, []]));
    for (const { name, options } of constraints) {
      const path = options.find(option => Object.entries(option).every(([k, n]) => ratings[k] >= n));
      for (const [k, n] of Object.entries(path)) {
        if (n === ratings[k] && !support[k].includes(name)) support[k].push(name);
      }
    }
    return { ok: true, ratings, support, ratingIncreases: cost(ratings), knownCost: knownCost(ratings) };
  }

  function maximize(input) {
    const budget = COST_RULE.ceiling;
    const required = solve({ ...input, knownBudget: budget });
    if (!required.ok) return required;
    const { attrs, caps, badges, dunkMode = 'DD' } = input;
    const value = (v, k) => k !== 'DUNK' ? v[k] : dunkMode === 'max' ? Math.max(v.DD, v.SD) : v[dunkMode];
    const tier = (v, badge) => {
      let t = 0;
      for (const rules of badge.tiers) {
        if (!rules.some(rule => rule.every(([k, n]) => value(v, k) >= n))) break;
        t++;
      }
      return t;
    };
    const score = v => badges.reduce((sum, b) => sum + tier(v, b), 0);
    // Below-90 costs are unknown: this is an optimistic partial-cost search, not a full budget.
    const seed = Object.fromEntries(attrs.map(k => [k, Math.max(required.ratings[k], Math.min(89, caps[k]))]));
    const rank = (a, b) => b.score - a.score || a.cost - b.cost;
    const state = v => ({ v, score: score(v), cost: knownCost(v) });
    let best = state(seed), beam = [best];
    const visited = new Set([attrs.map(k => seed[k]).join(',')]);
    // Keep several paths at each cost level so a cheap shared upgrade can beat a greedy choice.
    // Bounded heuristic: feasible under the working rule, not a global-optimum claim.
    for (let round = 0; round < 34 && beam.length; round++) {
      const next = new Map();
      for (const current of beam) for (const badge of badges) {
        const t = tier(current.v, badge);
        if (t === badge.tiers.length) continue;
        for (const rule of badge.tiers[t]) for (const option of alternatives(rule, dunkMode)) {
          const v = { ...current.v };
          for (const [k, n] of Object.entries(option)) v[k] = Math.max(v[k], n);
          if (attrs.some(k => v[k] > caps[k]) || knownCost(v) > budget) continue;
          const key = attrs.map(k => v[k]).join(',');
          if (visited.has(key)) continue;
          visited.add(key);
          const candidate = state(v);
          if (rank(candidate, best) < 0) best = candidate;
          const bucket = next.get(candidate.cost) || [];
          bucket.push(candidate); bucket.sort(rank);
          next.set(candidate.cost, bucket.slice(0, 3));
        }
      }
      beam = [...next.values()].flat();
    }
    const achieved = Object.fromEntries(badges.map(b => [b.name, tier(best.v, b)]).filter(([, t]) => t));
    // Trim all unneeded ratings after the search, preserving every achieved badge and user floor.
    const plan = solve({ ...input, targets: achieved, knownBudget: budget });
    if (!plan.ok) throw new Error('Could not retain achieved badge tiers');
    return { ...plan, minimumRatings: required.ratings, minimumKnownCost: required.knownCost,
      addedTiers: score(plan.ratings) - score(required.ratings), method: 'partial-cost heuristic', costRule: COST_RULE };
  }
  return { solve, maximize, knownCost, COST_RULE };
})();
if (typeof module !== 'undefined' && module.exports) module.exports = ThresholdPlanner;
