import { test } from "node:test";
import assert from "node:assert/strict";
import { Store } from "../src/core/store.js";

type S = { n: number };
type A = { type: "add"; k: number };
const reducer = (s: S, a: A) => ({ state: { n: s.n + a.k }, events: [{ kind: "add", detail: { k: a.k } }] });
const changer = (s: S) => ({ n: s.n * 10 });

test("dispatch updates state, logs events and notifies", () => {
  const seen: number[] = [];
  const store = new Store<S, A>({ n: 1 }, reducer, changer);
  store.subscribe((s, cause) => seen.push(s.n) && cause);
  store.dispatch({ type: "add", k: 2 });
  assert.equal(store.state.n, 3);
  assert.deepEqual(store.log.events().map((e) => e.kind), ["add"]);
  assert.deepEqual(seen, [3]);
});

test("changes are logged as page_change events", () => {
  const store = new Store<S, A>({ n: 1 }, reducer, changer);
  store.change({ type: "cosmetic", label: "b" });
  assert.equal(store.state.n, 10);
  assert.deepEqual(store.log.events()[0]?.detail, { change: "cosmetic" });
});

test("subscribers learn whether a change or an action caused the update", () => {
  const causes: string[] = [];
  const store = new Store<S, A>({ n: 1 }, reducer, changer);
  store.subscribe((_s, cause) => { causes.push(cause); });
  store.dispatch({ type: "add", k: 1 });
  store.change({ type: "cosmetic", label: "b" });
  assert.deepEqual(causes, ["add", "change"]);
});
