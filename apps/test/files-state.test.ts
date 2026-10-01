import { test } from "node:test";
import assert from "node:assert/strict";
import { initial, reduce, withChange, type FilesState } from "../src/files/state.js";
import type { Item } from "../src/core/types.js";

const items: Item[] = [
  { id: "f00", attrs: { name: "Budget tracker.xlsx", type: "spreadsheet", modified: 700 } },
  { id: "f01", attrs: { name: "Q3 sales report.pdf", type: "report", modified: 650 } },
];

function run(state: FilesState, ...actions: Parameters<typeof reduce>[1][]) {
  const events = [];
  for (const a of actions) {
    const r = reduce(state, a);
    state = r.state;
    events.push(...r.events);
  }
  return { state, events };
}

test("open shows the file details", () => {
  const { state, events } = run(initial(items), { type: "open", id: "f01" });
  assert.deepEqual(state.view, { name: "details", id: "f01" });
  assert.deepEqual(events, [{ kind: "open", itemId: "f01" }]);
});

test("sharing commits with the recipient typed", () => {
  const { state, events } = run(initial(items), { type: "open", id: "f01" }, { type: "share" },
    { type: "setTo", text: "kenji@example.com" }, { type: "send" });
  assert.deepEqual(state.view, { name: "shared", id: "f01", to: "kenji@example.com" });
  assert.deepEqual(events.at(-1), { kind: "share", itemId: "f01", commit: true, detail: { to: "kenji@example.com" } });
});

test("send without a recipient is refused", () => {
  const { events } = run(initial(items), { type: "open", id: "f01" }, { type: "share" }, { type: "send" });
  assert.equal(events.at(-1)?.kind, "share_refused");
  assert.ok(!events.some((e) => e.commit));
});

test("share outside the details view is invalid", () => {
  assert.equal(run(initial(items), { type: "share" }).events[0]?.kind, "invalid");
});

test("opening a missing file is invalid", () => {
  assert.equal(run(initial(items), { type: "open", id: "f09" }).events[0]?.kind, "invalid");
});

test("a rename shows on the open file", () => {
  const s = run(initial(items), { type: "open", id: "f01" }).state;
  const next = withChange(s, { type: "update", id: "f01", attrs: { name: "Q3 sales report (final).pdf" } });
  assert.equal(next.items[1]!.attrs.name, "Q3 sales report (final).pdf");
  assert.deepEqual(next.view, { name: "details", id: "f01" });
});

test("uploads land at the top of the list", () => {
  const up: Item = { id: "u0", attrs: { name: "Incident report.pdf", type: "report", modified: 758 } };
  const next = withChange(initial(items), { type: "insert", items: [up], position: 0 });
  assert.deepEqual(next.items.map((i) => i.id), ["u0", "f00", "f01"]);
});

test("a cosmetic change only sets the banner", () => {
  const next = withChange(initial(items), { type: "cosmetic", label: "storage_banner" });
  assert.equal(next.banner, "storage_banner");
  assert.deepEqual(next.items, items);
});
