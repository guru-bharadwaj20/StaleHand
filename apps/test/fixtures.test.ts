// The TypeScript resolver and change code must reach the same ground truth as Python on the shared fixtures.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { applyChange } from "../src/core/changes.js";
import { resolve } from "../src/core/resolve.js";
import type { Scenario } from "../src/core/types.js";

const fixtures = ["inbox", "shop", "files", "tickets"].flatMap((d) =>
  readFileSync(fileURLToPath(new URL(`../../../schema/fixtures/${d}.jsonl`, import.meta.url)), "utf8")
    .split("\n").filter(Boolean).map((l) => JSON.parse(l) as Scenario));

test("fixtures are loaded", () => assert.ok(fixtures.length > 50));

for (const s of fixtures) {
  test(`same targets as python: ${s.id}`, () => {
    let items = s.items;
    for (const c of s.changes) items = applyChange(items, c.change);
    assert.equal(resolve(s.items, s.criterion).target, s.derived!.stale_target);
    assert.equal(resolve(items, s.criterion).target, s.derived!.final_target);
  });
}
