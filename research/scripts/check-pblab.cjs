// Compare calculator predictions with PBLab observations without refitting.
// Run from any directory: node research/scripts/check-pblab.cjs [--summary]
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '../..');
const read = file => JSON.parse(fs.readFileSync(path.join(root, file), 'utf8'));
const model = read('src/model.json');
const data = read('research/data/pblab-validation.json');
const template = fs.readFileSync(path.join(root, 'src/template.html'), 'utf8');
assert(process.argv.slice(2).every(arg => arg === '--summary'), 'Unknown argument');
assert.deepEqual(model.attrs, data.attributeKeys, 'Fixture/model attribute order differs');
assert.equal(model.attrs.length, 22, 'Expected all 22 attributes');
assert.equal(new Set(model.attrs).size, 22, 'Duplicate model attribute');
assert(Array.isArray(data.profiles) && data.profiles.length, 'No observation profiles');

// Execute the existing calculation section, not a second copy of its formula.
// Fail explicitly if its source boundaries change during a future refactor.
const start = template.indexOf('const NAMES=');
const end = template.indexOf('// ---- badges', start);
assert(start >= 0 && end > start, 'Calculator source boundaries changed');
const logic = template.slice(start, end);
assert(logic.includes('function compute(b)'), 'Calculator function changed');
const context = vm.createContext({ MODEL: model });
vm.runInContext(logic + '\nthis.computeProfile = compute;', context, { timeout: 1000 });

let ratings = 0, exact = 0, maxError = 0, unflagged = 0;
const mismatches = [], identities = new Set();
for (const test of data.profiles) {
  const p = test.profile;
  assert(p && model.positions[p.pos], 'Unknown profile position');
  assert([p.H, p.WS, p.W].every(Number.isInteger), 'Invalid physical settings');
  assert(typeof p.A === 'string' && typeof p.B === 'string', 'Missing anomaly/body type');
  assert(['Right', 'Left'].includes(test.handedness), 'Missing handedness');
  assert(/^\d{4}-\d{2}-\d{2}$/.test(test.observedDate), 'Missing observation date');
  assert(Array.isArray(test.sources) && test.sources.length && test.sources.every(s => typeof s === 'string' && s), 'Missing source references');
  assert(Array.isArray(test.observed) && test.observed.length === model.attrs.length && test.observed.every(v => Number.isInteger(v) && v >= 25 && v <= 99), 'Invalid observed caps');
  const identity = JSON.stringify([p.pos, p.H, p.WS, p.W, p.A, p.B, test.handedness]);
  assert(!identities.has(identity), 'Duplicate exact profile');
  identities.add(identity);

  context.input = p;
  const predicted = vm.runInContext('computeProfile(input)', context, { timeout: 1000 });
  model.attrs.forEach((key, i) => {
    const value = predicted.v[key];
    assert(Number.isInteger(value) && value >= 25 && value <= 99, `Invalid prediction: ${key}`);
    const delta = value - test.observed[i];
    ratings++;
    exact += delta === 0;
    maxError = Math.max(maxError, Math.abs(delta));
    if (delta) {
      const flagged = predicted.alt[key] !== undefined;
      unflagged += !flagged;
      mismatches.push({ profile: p, handedness: test.handedness, attribute: key,
        observed: test.observed[i], predicted: value, delta, flagged,
        alternative: predicted.alt[key] ?? null, sources: test.sources });
    }
  });
}
const report = { profiles: data.profiles.length, ratings, exact,
  exactPercent: 100 * exact / ratings, maxError, unflagged };
if (!process.argv.includes('--summary')) report.mismatches = mismatches;
// Differences are diagnostics: an approximate fitted model need not match exactly.
// Invalid data or a changed calculator extraction fails with a nonzero exit code.
console.log(JSON.stringify(report, null, 2));
