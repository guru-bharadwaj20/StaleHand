// Group result rows and count outcomes. Pure functions, so the tables can be tested without a browser.
import type { Result } from "./rows.js";

export const OUTCOMES = ["success", "stale", "wrong_item", "wrong_detail", "aborted", "no_commit"] as const;

export interface Group {
  key: string[];
  n: number;
  counts: Record<string, number>;
  successRate: number;
  staleRate: number;
  falseAlarms: number;
  meanSeconds: number;
}

export function group(rows: Result[], by: ((r: Result) => string)[]): Group[] {
  const buckets = new Map<string, Result[]>();
  for (const r of rows) {
    const k = JSON.stringify(by.map((f) => f(r)));
    const b = buckets.get(k);
    if (b) b.push(r);
    else buckets.set(k, [r]);
  }
  return [...buckets.entries()]
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([k, rs]) => {
      const counts: Record<string, number> = Object.fromEntries(OUTCOMES.map((o) => [o, 0]));
      for (const r of rs) counts[r.outcome] = (counts[r.outcome] ?? 0) + 1;
      return {
        key: JSON.parse(k) as string[],
        n: rs.length,
        counts,
        successRate: (counts.success ?? 0) / rs.length,
        staleRate: (counts.stale ?? 0) / rs.length,
        falseAlarms: rs.filter((r) => r.false_alarm).length,
        meanSeconds: rs.reduce((s, r) => s + r.model_seconds, 0) / rs.length,
      };
    });
}

export function filterRows(rows: Result[], fields: Record<string, (r: Result) => string>,
                           chosen: Record<string, string>): Result[] {
  return rows.filter((r) => Object.entries(chosen).every(([f, v]) => !v || fields[f]?.(r) === v));
}

export function distinct(rows: Result[], f: (r: Result) => string): string[] {
  return [...new Set(rows.map(f))].sort();
}

export const pct = (x: number): string => `${(100 * x).toFixed(1)}%`;
