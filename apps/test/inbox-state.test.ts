import { test } from "node:test";
import assert from "node:assert/strict";
import { initial, reduce, type InboxState } from "../src/inbox/state.js";
import type { Item } from "../src/core/types.js";

const items: Item[] = [
  { id: "m00", attrs: { sender: "Kim", subject: "Lunch", received: 700 } },
  { id: "m01", attrs: { sender: "Sam", subject: "Invoice", received: 650 } },
];

function run(state: InboxState, ...actions: Parameters<typeof reduce>[1][]) {
  const events = [];
  for (const a of actions) {
    const r = reduce(state, a);
    state = r.state;
    events.push(...r.events);
  }
  return { state, events };
}

test("opening a mail shows it and logs an open event", () => {
  const { state, events } = run(initial(items), { type: "open", id: "m01" });
  assert.deepEqual(state.view, { name: "open", id: "m01" });
  assert.deepEqual(events, [{ kind: "open", itemId: "m01" }]);
});

test("forward flow sends to the typed recipient", () => {
  const { state, events } = run(initial(items), { type: "open", id: "m01" }, { type: "forward" },
    { type: "setTo", text: "laura@example.com" }, { type: "send" });
  assert.equal(state.view.name, "sent");
  assert.deepEqual(events.at(-1), { kind: "send", itemId: "m01", commit: true, detail: { mode: "forward", to: "laura@example.com" } });
});

test("reply flow sends to the original sender", () => {
  const { events } = run(initial(items), { type: "open", id: "m01" }, { type: "reply" },
    { type: "setBody", text: "Thanks!" }, { type: "send" });
  assert.deepEqual(events.at(-1)?.detail, { mode: "reply", to: "Sam", body: "Thanks!" });
});

test("send without a recipient is refused", () => {
  const { state, events } = run(initial(items), { type: "open", id: "m01" }, { type: "forward" }, { type: "send" });
  assert.equal(state.view.name, "compose");
  assert.equal(events.at(-1)?.kind, "send_refused");
});

test("opening an unknown id is ignored and logged", () => {
  const { state, events } = run(initial(items), { type: "open", id: "zz" });
  assert.equal(state.view.name, "list");
  assert.equal(events[0]?.kind, "invalid");
});

test("back returns to the list", () => {
  const { state } = run(initial(items), { type: "open", id: "m01" }, { type: "back" });
  assert.equal(state.view.name, "list");
});
