import { test } from "node:test";
import assert from "node:assert/strict";
import { initial, reduce, withChange } from "../src/calendar/state.js";
import type { Item } from "../src/core/types.js";

const items: Item[] = [
  { id: "e00", attrs: { title: "Design sync", with: "Kenji Sato", start: 570 } },
  { id: "e01", attrs: { title: "Budget check-in", with: "Grace Kim", start: 630 } },
];

test("joining an open meeting commits", () => {
  let s = reduce(initial(items), { type: "open", id: "e01" }).state;
  const r = reduce(s, { type: "join" });
  s = r.state;
  assert.deepEqual(s.view, { name: "joined", id: "e01" });
  assert.deepEqual(r.events, [{ kind: "join", itemId: "e01", commit: true, detail: { start: 630 } }]);
});

test("a cancelled meeting cannot be joined", () => {
  const s = reduce(initial(items), { type: "open", id: "e00" }).state;
  const r = reduce(withChange(s, { type: "remove", ids: ["e00"] }), { type: "join" });
  assert.equal(r.events[0]?.kind, "join_refused");
});

test("join from the agenda is invalid", () => {
  assert.equal(reduce(initial(items), { type: "join" }).events[0]?.kind, "invalid");
});

test("a reschedule moves the meeting in the agenda", () => {
  const next = withChange(initial(items), { type: "update", id: "e00", attrs: { start: 700 } });
  assert.deepEqual(next.items.map((i) => i.id), ["e01", "e00"]);
});
