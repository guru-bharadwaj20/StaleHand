import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { FIELDS, domainOf, loadJsonl, makeValidator, type Result } from "../src/rows.js";
import { distinct, filterRows, group, pct } from "../src/summary.js";

const schema = JSON.parse(readFileSync(fileURLToPath(new URL("../../../schema/result.schema.json", import.meta.url)), "utf8"));
const validate = makeValidator(schema);

function row(over: Partial<Result> = {}): Result {
  return {
    scenario_id: "inbox-relative-000-L1", guard: "none", architecture: "hierarchical", kind: "relative", variant: "L1",
    change_kind: "relevant", outcome: "success", target: "n0", correct_target: "n0", stale_target: "m03",
    end_reason: "done", fired: 0, false_alarm: false, planner_calls: 2, executor_calls: 3, checker_calls: 0,
    model_seconds: 4.5, env_steps: 3, parse_failures: 0, commit_step: 3, commit_before_change: false, ...over,
  };
}

const jsonl = (...rows: unknown[]) => rows.map((r) => JSON.stringify(r)).join("\n");

test("valid rows load and invalid ones are reported with their line", () => {
  const bad = { ...row(), outcome: "great" };
  const { scenario_id: _drop, ...missing } = row();
  const got = loadJsonl(`${jsonl(row(), bad)}\n\n${jsonl(missing)}\n{oops`, "a.jsonl", validate);
  assert.equal(got.rows.length, 1);
  assert.deepEqual(got.problems.map((p) => p.line), [2, 4, 5]);
  assert.match(got.problems[0]!.message, /outcome/);
  assert.match(got.problems[2]!.message, /not JSON/);
});

test("the stats fixture rows are not full results and are rejected", () => {
  const text = readFileSync(fileURLToPath(new URL("../../../schema/fixtures/results_pair.jsonl", import.meta.url)), "utf8");
  const got = loadJsonl(text, "results_pair.jsonl", validate);
  assert.equal(got.rows.length, 0);
  assert.ok(got.problems.length > 0);
});

test("grouping counts outcomes and rates per key", () => {
  const rows = [row(), row({ outcome: "stale" }), row({ guard: "rule_subtask" }), row({ guard: "rule_subtask", false_alarm: true, model_seconds: 1.5 })];
  const g = group(rows, [FIELDS.guard!]);
  assert.deepEqual(g.map((x) => x.key), [["none"], ["rule_subtask"]]);
  assert.equal(g[0]!.n, 2);
  assert.equal(g[0]!.successRate, 0.5);
  assert.equal(g[0]!.staleRate, 0.5);
  assert.equal(g[1]!.falseAlarms, 1);
  assert.equal(g[1]!.meanSeconds, 3);
});

test("filters keep matching rows and ignore empty choices", () => {
  const rows = [row(), row({ scenario_id: "shop-cheapest-000-L1" })];
  assert.equal(filterRows(rows, FIELDS, { domain: "shop", guard: "" }).length, 1);
  assert.deepEqual(distinct(rows, domainOf), ["inbox", "shop"]);
});

test("executor comes from run provenance when present", () => {
  assert.equal(FIELDS.executor!(row({ run: { executor: "internvl3.5-8b" } })), "internvl3.5-8b");
  assert.equal(FIELDS.executor!(row()), "");
});

test("percentages have one decimal", () => assert.equal(pct(0.8111), "81.1%"));
