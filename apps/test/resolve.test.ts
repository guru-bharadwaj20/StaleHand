import { test } from "node:test";
import assert from "node:assert/strict";
import { resolve } from "../src/core/resolve.js";
import type { Item } from "../src/core/types.js";

const mail = (id: string, sender: string, received?: number): Item => ({ id, attrs: { sender, received } });
const inbox = [mail("a", "Sam", 10), mail("b", "Kim", 20), mail("c", "Sam", 30)];

test("filters select the single match", () => {
  assert.deepEqual(resolve(inbox, { filters: [["sender", "Kim"]], order: null }), { target: "b", status: "unique" });
});

test("no match gives none", () => {
  assert.equal(resolve(inbox, { filters: [["sender", "Zed"]], order: null }).status, "none");
});

test("two matches without order are ambiguous", () => {
  assert.equal(resolve(inbox, { filters: [["sender", "Sam"]], order: null }).status, "ambiguous");
});

test("newest first picks the latest", () => {
  const r = resolve(inbox, { filters: [["sender", "Sam"]], order: { field: "received", descending: true } });
  assert.equal(r.target, "c");
});

test("ascending picks the minimum", () => {
  assert.equal(resolve(inbox, { filters: [], order: { field: "received", descending: false } }).target, "a");
});

test("tie at the top is ambiguous", () => {
  const items = [mail("x", "Sam", 5), mail("y", "Sam", 5)];
  assert.equal(resolve(items, { filters: [], order: { field: "received", descending: true } }).status, "ambiguous");
});

test("items missing the order field never win", () => {
  const items = [mail("x", "Sam"), mail("y", "Sam", 1)];
  assert.equal(resolve(items, { filters: [], order: { field: "received", descending: true } }).target, "y");
});
