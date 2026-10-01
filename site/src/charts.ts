// Per-guard numbers for the main results and inline SVG bar charts. Pure functions over loaded result rows,
// so the charts can be tested without a browser and always follow the explorer's filters.
import type { Result } from "./rows.js";

// same definition as src/stalehand/report/tables.py: a guard firing is only surely unwarranted on these
export const HARMLESS = ["none", "irrelevant"] as const;

export interface GuardStats {
  guard: string;
  n: number;
  relevant: number;
  stale: number;
  staleRate: number | null; // stale / relevant-change episodes
  harmless: number;
  falseAlarms: number;
  falseAlarmRate: number | null; // false alarms / harmless-change episodes
  meanPlannerCalls: number;
  meanModelSeconds: number;
}

export function guardStats(rows: Result[]): GuardStats[] {
  const by = new Map<string, Result[]>();
  for (const r of rows) {
    const b = by.get(r.guard);
    if (b) b.push(r);
    else by.set(r.guard, [r]);
  }
  return [...by.keys()].sort().map((guard) => {
    const rs = by.get(guard)!;
    const rel = rs.filter((r) => r.change_kind === "relevant");
    const harm = rs.filter((r) => (HARMLESS as readonly string[]).includes(r.change_kind));
    const stale = rel.filter((r) => r.outcome === "stale").length;
    const falseAlarms = harm.filter((r) => r.false_alarm).length;
    const mean = (f: (r: Result) => number) => rs.reduce((s, r) => s + f(r), 0) / rs.length;
    return {
      guard, n: rs.length, relevant: rel.length, stale, staleRate: rel.length ? stale / rel.length : null,
      harmless: harm.length, falseAlarms, falseAlarmRate: harm.length ? falseAlarms / harm.length : null,
      meanPlannerCalls: mean((r) => Number(r.planner_calls)), meanModelSeconds: mean((r) => r.model_seconds),
    };
  });
}

export interface Bar {
  label: string;
  value: number | null; // null: no episodes to compute it from
  text: string; // value as shown next to the bar
}

const esc = (s: string) => s.replace(/[&<>"']/g, (c) => `&${({ "&": "amp", "<": "lt", ">": "gt", '"': "quot", "'": "#39" })[c]};`);

// Horizontal bar chart. max fixes the scale (1 for rates); otherwise the largest value is used.
export function barChart(title: string, bars: Bar[], max?: number): string {
  const rowH = 24, labelW = 170, barW = 260, valueW = 110, top = 28;
  const width = labelW + barW + valueW, height = top + rowH * bars.length + 6;
  const scale = max ?? Math.max(0, ...bars.map((b) => b.value ?? 0));
  const id = `t${Math.abs([...title].reduce((h, c) => (h * 31 + c.charCodeAt(0)) | 0, 7))}`;
  const rows = bars.map((b, i) => {
    const y = top + i * rowH;
    const w = b.value === null || scale <= 0 ? 0 : Math.max(b.value > 0 ? 1 : 0, (b.value / scale) * barW);
    return `<g role="listitem" aria-label="${esc(`${b.label}: ${b.text}`)}">`
      + `<text class="lbl" x="${labelW - 8}" y="${y + 16}" text-anchor="end">${esc(b.label)}</text>`
      + `<rect class="bar" x="${labelW}" y="${y + 4}" width="${w.toFixed(1)}" height="${rowH - 8}" rx="2"/>`
      + `<text class="val" x="${labelW + w + 6}" y="${y + 16}">${esc(b.text)}</text></g>`;
  }).join("");
  return `<svg class="chart" role="img" aria-labelledby="${id}" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">`
    + `<title id="${id}">${esc(title)}</title>`
    + `<text class="ttl" x="0" y="16">${esc(title)}</text>`
    + `<line class="axis" x1="${labelW}" y1="${top}" x2="${labelW}" y2="${height - 4}"/>`
    + `<g role="list">${rows}</g></svg>`;
}

const pct = (x: number) => `${(100 * x).toFixed(1)}%`;

export function mainCharts(rows: Result[]): string[] {
  const s = guardStats(rows);
  return [
    barChart("Stale rate on relevant changes", s.map((g) => ({
      label: g.guard, value: g.staleRate, text: g.staleRate === null ? "no episodes" : `${pct(g.staleRate)} (${g.stale}/${g.relevant})` })), 1),
    barChart("False-alarm rate on harmless changes", s.map((g) => ({
      label: g.guard, value: g.falseAlarmRate,
      text: g.falseAlarmRate === null ? "no episodes" : `${pct(g.falseAlarmRate)} (${g.falseAlarms}/${g.harmless})` })), 1),
    barChart("Mean planner calls per episode", s.map((g) => ({
      label: g.guard, value: g.meanPlannerCalls, text: `${g.meanPlannerCalls.toFixed(2)} (n=${g.n})` }))),
    barChart("Mean model seconds per episode", s.map((g) => ({
      label: g.guard, value: g.meanModelSeconds, text: `${g.meanModelSeconds.toFixed(1)} s (n=${g.n})` }))),
  ];
}
