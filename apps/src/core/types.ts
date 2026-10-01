// Mirrors schema/scenario.schema.json. Python writes these rows; the apps read them.

export type Attrs = Record<string, unknown>;

export interface Item {
  id: string;
  attrs: Attrs;
}

export interface Order {
  field: string;
  descending: boolean;
}

export interface Criterion {
  filters: [string, unknown][];
  order: Order | null;
}

export type Change =
  | { type: "insert"; items: Item[]; position: number }
  | { type: "remove"; ids: string[] }
  | { type: "update"; id: string; attrs: Attrs }
  | { type: "sort"; field: string; descending: boolean }
  | { type: "cosmetic"; label: string };

export interface ScheduledChange {
  step: number;
  change: Change;
}

export type ChangeKind = "none" | "irrelevant" | "relevant" | "target_removed";

export interface Scenario {
  id: string;
  domain: string;
  seed: number;
  task: string;
  criterion: Criterion;
  items: Item[];
  changes: ScheduledChange[];
  meta: Record<string, unknown>;
  derived?: { stale_target: string; final_target: string | null; change_kind: ChangeKind };
}
