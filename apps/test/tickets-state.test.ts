import { test } from "node:test";
import assert from "node:assert/strict";
import { initial, reduce, withChange, type TicketsState } from "../src/tickets/state.js";
import type { Item } from "../src/core/types.js";

const items: Item[] = [
  { id: "t1002", attrs: { key: "T-1002", priority: "high", created: 700, assignee: null } },
  { id: "t1001", attrs: { key: "T-1001", priority: "low", created: 650, assignee: null } },
];

function run(state: TicketsState, ...actions: Parameters<typeof reduce>[1][]) {
  const events = [];
  for (const a of actions) {
    const r = reduce(state, a);
    state = r.state;
    events.push(...r.events);
  }
  return { state, events };
}

test("assigning commits with the assignee typed", () => {
  const { state, events } = run(initial(items), { type: "open", id: "t1002" }, { type: "assign" },
    { type: "setTo", text: "Grace Kim" }, { type: "save" });
  assert.deepEqual(state.view, { name: "assigned", id: "t1002", to: "Grace Kim" });
  assert.equal(state.items[0]!.attrs.assignee, "Grace Kim");
  assert.deepEqual(events.at(-1), { kind: "assign", itemId: "t1002", commit: true, detail: { to: "Grace Kim" } });
});

test("save without an assignee is refused", () => {
  const { events } = run(initial(items), { type: "open", id: "t1002" }, { type: "assign" }, { type: "save" });
  assert.equal(events.at(-1)?.kind, "assign_refused");
});

test("a closed ticket cannot be assigned", () => {
  const s = run(initial(items), { type: "open", id: "t1002" }, { type: "assign" }, { type: "setTo", text: "Grace Kim" }).state;
  const { events } = run(withChange(s, { type: "remove", ids: ["t1002"] }), { type: "save" });
  assert.equal(events[0]?.kind, "assign_refused");
  assert.ok(!events.some((e) => e.commit));
});

test("assign outside a ticket is invalid", () => {
  assert.equal(run(initial(items), { type: "assign" }).events[0]?.kind, "invalid");
});

test("a priority change shows in the queue", () => {
  const next = withChange(initial(items), { type: "update", id: "t1001", attrs: { priority: "high" } });
  assert.equal(next.items[1]!.attrs.priority, "high");
});
