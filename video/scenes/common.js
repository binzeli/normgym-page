// Shared timing helpers for the scene pages. Each scene defines window.DURATION and window.seek(t).
const clamp = (x) => Math.max(0, Math.min(1, x));
const lerp = (a, b, u) => a + (b - a) * u;
const p = (t, a, b) => clamp((t - a) / (b - a));
const smooth = (x) => { x = clamp(x); return x * x * (3 - 2 * x); };
const back = (x) => { x = clamp(x); const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2; };

// Fade an element in place over [a, a+d]; optional fade out over [b, b+d].
function enter(node, t, a, { d = 0.6, b = Infinity } = {}) {
  const out = b === Infinity ? 0 : smooth(p(t, b, b + d));
  const u = smooth(p(t, a, a + d)) * (1 - out);
  node.style.opacity = u;
  return u;
}
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
