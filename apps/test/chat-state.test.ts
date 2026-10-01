import { test } from "node:test";
import assert from "node:assert/strict";
import { initial, reduce, withChange, type ChatState } from "../src/chat/state.js";
import type { Item } from "../src/core/types.js";

const items: Item[] = [
  { id: "c00", attrs: { sender: "Grace Kim", topic: "Q3 budget", sent: 700 } },
  { id: "c01", attrs: { sender: "Kenji Sato", topic: "invoice", sent: 690 } },
];

function run(state: ChatState, ...actions: Parameters<typeof reduce>[1][]) {
  const events = [];
  for (const a of actions) {
    const r = reduce(state, a);
    state = r.state;
    events.push(...r.events);
  }
  return { state, events };
}

test("replying commits in reply mode with the body", () => {
  const { state, events } = run(initial(items), { type: "open", id: "c01" }, { type: "setBody", text: "Thanks!" }, { type: "send" });
  assert.deepEqual(state.view, { name: "sent", id: "c01" });
  assert.deepEqual(events.at(-1), { kind: "send", itemId: "c01", commit: true, detail: { mode: "reply", body: "Thanks!" } });
});

test("an empty reply is refused", () => {
  const { events } = run(initial(items), { type: "open", id: "c01" }, { type: "send" });
  assert.equal(events.at(-1)?.kind, "send_refused");
});

test("send without a reply box is invalid", () => {
  assert.equal(run(initial(items), { type: "send" }).events[0]?.kind, "invalid");
});

test("an edit changes the message in place", () => {
  const next = withChange(initial(items), { type: "update", id: "c00", attrs: { topic: "invoice", edited: true } });
  assert.equal(next.items[0]!.attrs.edited, true);
  assert.equal(next.items.length, 2);
});
