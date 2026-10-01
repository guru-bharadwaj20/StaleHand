import { test } from "node:test";
import assert from "node:assert/strict";
import { ActionLog } from "../src/core/log.js";

test("events keep order and get sequence numbers", () => {
  const log = new ActionLog(() => 1000);
  log.record({ kind: "open", itemId: "m01" });
  log.record({ kind: "send", itemId: "m01", detail: { to: "a@example.com" } });
  assert.deepEqual(log.events().map((e) => [e.seq, e.kind]), [[0, "open"], [1, "send"]]);
  assert.equal(log.events()[0]!.t, 1000);
});

test("returned events are copies", () => {
  const log = new ActionLog();
  log.record({ kind: "open", itemId: "m01" });
  log.events().pop();
  assert.equal(log.events().length, 1);
});

test("committing events are filtered", () => {
  const log = new ActionLog();
  log.record({ kind: "open", itemId: "m01" });
  log.record({ kind: "add_to_cart", itemId: "p02", commit: true });
  assert.deepEqual(log.commits().map((e) => e.itemId), ["p02"]);
});
