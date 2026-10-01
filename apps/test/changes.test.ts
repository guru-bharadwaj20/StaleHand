import { test } from "node:test";
import assert from "node:assert/strict";
import { applyChange } from "../src/core/changes.js";
import type { Item } from "../src/core/types.js";

const base: Item[] = [{ id: "a", attrs: { v: 1 } }, { id: "b", attrs: { v: 2 } }, { id: "c", attrs: { v: 3 } }];
const ids = (items: Item[]) => items.map((i) => i.id);

test("insert at the top by default position", () => {
  assert.deepEqual(ids(applyChange(base, { type: "insert", items: [{ id: "n", attrs: {} }], position: 0 })), ["n", "a", "b", "c"]);
});

test("insert duplicate id throws", () => {
  assert.throws(() => applyChange(base, { type: "insert", items: [{ id: "a", attrs: {} }], position: 0 }));
});

test("remove drops ids and rejects missing ones", () => {
  assert.deepEqual(ids(applyChange(base, { type: "remove", ids: ["b"] })), ["a", "c"]);
  assert.throws(() => applyChange(base, { type: "remove", ids: ["zz"] }));
});

test("update merges attributes without mutating input", () => {
  const out = applyChange(base, { type: "update", id: "b", attrs: { v: 20 } });
  assert.equal(out[1]!.attrs.v, 20);
  assert.equal(base[1]!.attrs.v, 2);
});

test("sort orders and puts missing values last", () => {
  const items: Item[] = [{ id: "x", attrs: {} }, ...base];
  assert.deepEqual(ids(applyChange(items, { type: "sort", field: "v", descending: true })), ["c", "b", "a", "x"]);
});

test("cosmetic keeps items", () => {
  assert.deepEqual(applyChange(base, { type: "cosmetic", label: "banner" }), base);
});
