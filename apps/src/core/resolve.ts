// Ground truth resolver; must agree with src/stalehand/scenarios/resolve.py (checked against shared fixtures).
import type { Criterion, Item } from "./types.js";

export interface Resolution {
  target: string | null;
  status: "unique" | "none" | "ambiguous";
}

const present = (v: unknown): v is number | string => v !== undefined && v !== null;

export function resolve(items: readonly Item[], criterion: Criterion): Resolution {
  let found = items.filter((it) => criterion.filters.every(([k, v]) => it.attrs[k] === v));
  if (criterion.order) {
    const { field, descending } = criterion.order;
    found = found.filter((it) => present(it.attrs[field]));
    if (found.length === 0) return { target: null, status: "none" };
    const values = found.map((it) => it.attrs[field] as number);
    const best = descending ? Math.max(...values) : Math.min(...values);
    found = found.filter((it) => it.attrs[field] === best);
  }
  if (found.length === 0) return { target: null, status: "none" };
  if (found.length > 1) return { target: null, status: "ambiguous" };
  return { target: found[0]!.id, status: "unique" };
}
