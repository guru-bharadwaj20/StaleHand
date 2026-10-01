import { test } from "node:test";
import assert from "node:assert/strict";
import { initial, reduce, withChange, type ShopState } from "../src/shop/state.js";
import type { Item } from "../src/core/types.js";

const items: Item[] = [
  { id: "p00", attrs: { name: "Glide", price: 499 } },
  { id: "p01", attrs: { name: "Aether", price: 299 } },
];

function run(state: ShopState, ...actions: Parameters<typeof reduce>[1][]) {
  const events = [];
  for (const a of actions) {
    const r = reduce(state, a);
    state = r.state;
    events.push(...r.events);
  }
  return { state, events };
}

test("open shows the product page", () => {
  const { state, events } = run(initial(items), { type: "open", id: "p01" });
  assert.deepEqual(state.view, { name: "product", id: "p01" });
  assert.deepEqual(events, [{ kind: "open", itemId: "p01" }]);
});

test("adding to cart commits with the price seen", () => {
  const { state, events } = run(initial(items), { type: "open", id: "p01" }, { type: "add" });
  assert.deepEqual(state.view, { name: "added", id: "p01" });
  assert.deepEqual(state.cart, ["p01"]);
  assert.deepEqual(events.at(-1), { kind: "add_to_cart", itemId: "p01", commit: true, detail: { price: 299 } });
});

test("add outside a product page is invalid", () => {
  assert.equal(run(initial(items), { type: "add" }).events[0]?.kind, "invalid");
});

test("a sold-out product cannot be added", () => {
  const s = run(initial(items), { type: "open", id: "p01" }).state;
  const gone = withChange(s, { type: "remove", ids: ["p01"] });
  const { state, events } = run(gone, { type: "add" });
  assert.equal(events[0]?.kind, "add_refused");
  assert.deepEqual(state.cart, []);
});

test("price updates show on the open product", () => {
  const s = run(initial(items), { type: "open", id: "p00" }).state;
  const next = withChange(s, { type: "update", id: "p00", attrs: { price: 199 } });
  assert.equal(next.items[0]!.attrs.price, 199);
});
