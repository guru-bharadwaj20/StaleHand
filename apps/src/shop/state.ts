// Shop app as a pure state machine: results list -> product page -> added to cart.
import { applyChange } from "../core/changes.js";
import type { ActionEvent } from "../core/log.js";
import type { Change, Item } from "../core/types.js";

export type View = { name: "list" } | { name: "product"; id: string } | { name: "added"; id: string };

export interface ShopState {
  items: Item[];
  view: View;
  cart: string[];
  banner: string | null;
}

export type ShopAction = { type: "open"; id: string } | { type: "back" } | { type: "add" };

export const initial = (items: Item[]): ShopState => ({ items, view: { name: "list" }, cart: [], banner: null });

export function reduce(state: ShopState, action: ShopAction): { state: ShopState; events: ActionEvent[] } {
  const v = state.view;
  switch (action.type) {
    case "open":
      if (!state.items.some((i) => i.id === action.id)) {
        return { state, events: [{ kind: "invalid", detail: { reason: `no product ${action.id}` } }] };
      }
      return { state: { ...state, view: { name: "product", id: action.id } }, events: [{ kind: "open", itemId: action.id }] };
    case "back":
      return { state: { ...state, view: { name: "list" } }, events: [{ kind: "back" }] };
    case "add": {
      if (v.name !== "product") return { state, events: [{ kind: "invalid", detail: { reason: "add needs a product page" } }] };
      const item = state.items.find((i) => i.id === v.id);
      if (!item) return { state, events: [{ kind: "add_refused", itemId: v.id, detail: { reason: "sold out" } }] };
      return {
        state: { ...state, view: { name: "added", id: v.id }, cart: [...state.cart, v.id] },
        events: [{ kind: "add_to_cart", itemId: v.id, commit: true, detail: { price: item.attrs.price } }],
      };
    }
  }
}

export function withChange(state: ShopState, change: Change): ShopState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: applyChange(state.items, change) };
}
