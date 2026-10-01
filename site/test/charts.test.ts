import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { FIELDS, loadJsonl, makeValidator, type Result } from "../src/rows.js";
import { filterRows } from "../src/summary.js";
import { barChart, guardStats, mainCharts } from "../src/charts.js";

const repo = (p: string) => fileURLToPath(new URL(`../../../${p}`, import.meta.url));
const validate = makeValidator(JSON.parse(readFileSync(repo("schema/result.schema.json"), "utf8")));

function row(over: Partial<Result> = {}): Result {
  return {
    scenario_id: "inbox-relative-000-L1", guard: "none", architecture: "hierarchical", kind: "relative", variant: "L1",
    change_kind: "relevant", outcome: "success", target: "n0", correct_target: "n0", stale_target: "m03",
    end_reason: "done", fired: 0, false_alarm: false, planner_calls: 2, executor_calls: 3, checker_calls: 0,
    model_seconds: 4, env_steps: 3, parse_failures: 0, commit_step: 3, commit_before_change: false, ...over,
  };
}

test("stale rate counts only relevant changes, false alarms only harmless ones", () => {
  const s = guardStats([
    row({ outcome: "stale" }), row(), row({ change_kind: "none", outcome: "stale", false_alarm: true }),
    row({ change_kind: "irrelevant" }), row({ change_kind: "unrelated_kind", false_alarm: true }),
    row({ guard: "rule", planner_calls: 5, model_seconds: 10 }),
  ]);
  assert.deepEqual(s.map((g) => g.guard), ["none", "rule"]);
  const [none, rule] = s as [typeof s[0], typeof s[0]];
  assert.equal(none.staleRate, 0.5);
  assert.equal(none.falseAlarmRate, 0.5);
  assert.equal(none.meanPlannerCalls, 2);
  assert.equal(rule.falseAlarmRate, null);
  assert.equal(rule.meanModelSeconds, 10);
});

test("bar chart is labelled, escapes text and scales bars", () => {
  const svg = barChart("A <b>", [{ label: "x&y", value: 0.5, text: "50%" }, { label: "z", value: null, text: "no episodes" }], 1);
  assert.match(svg, /role="img"/);
  assert.match(svg, /<title id="t-?\d+">A &lt;b&gt;<\/title>/);
  assert.match(svg, /aria-label="x&amp;y: 50%"/);
  assert.match(svg, /width="130.0"/);
  assert.doesNotMatch(svg, /<b>/);
});

test("real pilot results produce charts that follow filters", () => {
  const root = repo("results/vivian-4090/pilot");
  if (!existsSync(root)) return;
  const rows: Result[] = [];
  for (const d of readdirSync(root)) {
    const f = `${root}/${d}/results.jsonl`;
    if (!existsSync(f)) continue;
    const got = loadJsonl(readFileSync(f, "utf8"), f, validate);
    assert.deepEqual(got.problems, []);
    rows.push(...got.rows);
  }
  assert.ok(rows.length > 0);
  const s = guardStats(rows);
  for (const g of s) {
    for (const r of [g.staleRate, g.falseAlarmRate]) if (r !== null) assert.ok(r >= 0 && r <= 1);
    assert.ok(g.meanModelSeconds > 0);
  }
  assert.equal(s.reduce((n, g) => n + g.n, 0), rows.length);
  const shop = filterRows(rows, FIELDS, { domain: "shop" });
  assert.equal(guardStats(shop).reduce((n, g) => n + g.n, 0), shop.length);
  assert.equal(mainCharts(rows).length, 4);
  console.log(s.map((g) => `${g.guard} n=${g.n} stale=${g.stale}/${g.relevant} fa=${g.falseAlarms}/${g.harmless} planner=${g.meanPlannerCalls.toFixed(2)} sec=${g.meanModelSeconds.toFixed(1)}`).join("\n"));
});
