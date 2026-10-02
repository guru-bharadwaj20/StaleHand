// Parse and validate result JSONL. Every number the site shows comes from rows that passed the schema.
import { Ajv2020 } from "ajv/dist/2020.js";

export type Result = Record<string, unknown> & {
  scenario_id: string;
  guard: string;
  architecture: string;
  kind: string | null;
  variant: string | null;
  change_kind: string;
  outcome: string;
  fired: number;
  false_alarm: boolean;
  model_seconds: number;
  run?: Record<string, unknown>;
  run_set?: string; // set by the explorer: "<machine>/<set>" for built-in sets, else the file name
};

export interface Problem {
  source: string;
  line: number;
  message: string;
}

export interface Loaded {
  rows: Result[];
  problems: Problem[];
}

export type Validator = (row: unknown) => string | null;

export function makeValidator(schema: object): Validator {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  const check = ajv.compile(schema);
  return (row) => {
    if (check(row)) return null;
    return (check.errors ?? []).map((e) => `${e.instancePath || "row"} ${e.message ?? "is invalid"}`).join("; ");
  };
}

// one bad line must not hide the good ones, so problems are collected per line
export function loadJsonl(text: string, source: string, validate: Validator, runSet = source): Loaded {
  const rows: Result[] = [];
  const problems: Problem[] = [];
  text.split(/\r?\n/).forEach((raw, i) => {
    if (!raw.trim()) return;
    let row: unknown;
    try {
      row = JSON.parse(raw);
    } catch (e) {
      problems.push({ source, line: i + 1, message: `not JSON: ${(e as Error).message}` });
      return;
    }
    const err = validate(row);
    if (err) problems.push({ source, line: i + 1, message: err });
    else rows.push({ ...(row as Result), run_set: runSet });
  });
  return { rows, problems };
}

// scenario ids look like "<domain>-<kind>-<index>-<variant>"
export const domainOf = (r: Result): string => r.scenario_id.split("-", 1)[0] ?? "";

const runField = (r: Result, key: string): string => {
  const v = r.run?.[key];
  return v === undefined || v === null ? "" : String(v);
};

export const FIELDS: Record<string, (r: Result) => string> = {
  run_set: (r) => r.run_set ?? "",
  domain: domainOf,
  guard: (r) => r.guard,
  architecture: (r) => r.architecture,
  kind: (r) => r.kind ?? "",
  variant: (r) => r.variant ?? "",
  change_kind: (r) => r.change_kind,
  outcome: (r) => r.outcome,
  executor: (r) => runField(r, "executor"),
};
