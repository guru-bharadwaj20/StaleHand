// Tickets app as a pure state machine: queue -> ticket -> assign form -> assigned.
import { applyChange } from "../core/changes.js";
import type { ActionEvent } from "../core/log.js";
import type { Change, Item } from "../core/types.js";

export type View =
  | { name: "list" }
  | { name: "ticket"; id: string }
  | { name: "assign"; id: string; to: string }
  | { name: "assigned"; id: string; to: string };

export interface TicketsState {
  items: Item[];
  view: View;
  banner: string | null;
}

export type TicketsAction =
  | { type: "open"; id: string }
  | { type: "back" }
  | { type: "assign" }
  | { type: "setTo"; text: string }
  | { type: "save" };

export interface Step {
  state: TicketsState;
  events: ActionEvent[];
}

export const initial = (items: Item[]): TicketsState => ({ items, view: { name: "list" }, banner: null });

const invalid = (state: TicketsState, reason: string): Step => ({ state, events: [{ kind: "invalid", detail: { reason } }] });

export function reduce(state: TicketsState, action: TicketsAction): Step {
  const v = state.view;
  switch (action.type) {
    case "open":
      if (!state.items.some((i) => i.id === action.id)) return invalid(state, `no ticket ${action.id}`);
      return { state: { ...state, view: { name: "ticket", id: action.id } }, events: [{ kind: "open", itemId: action.id }] };
    case "back":
      return { state: { ...state, view: { name: "list" } }, events: [{ kind: "back" }] };
    case "assign":
      if (v.name !== "ticket") return invalid(state, "assign needs an open ticket");
      return { state: { ...state, view: { name: "assign", id: v.id, to: "" } }, events: [{ kind: "assign_form", itemId: v.id }] };
    case "setTo":
      if (v.name !== "assign") return invalid(state, "typing needs the assign form");
      return { state: { ...state, view: { ...v, to: action.text } }, events: [{ kind: "setTo", itemId: v.id, detail: { text: action.text } }] };
    case "save": {
      if (v.name !== "assign") return invalid(state, "save needs the assign form");
      if (!v.to.trim()) return { state, events: [{ kind: "assign_refused", itemId: v.id, detail: { reason: "no assignee" } }] };
      if (!state.items.some((i) => i.id === v.id)) {
        return { state, events: [{ kind: "assign_refused", itemId: v.id, detail: { reason: "ticket closed" } }] };
      }
      const items = state.items.map((i) => (i.id === v.id ? { ...i, attrs: { ...i.attrs, assignee: v.to } } : i));
      return {
        state: { ...state, items, view: { name: "assigned", id: v.id, to: v.to } },
        events: [{ kind: "assign", itemId: v.id, commit: true, detail: { to: v.to } }],
      };
    }
  }
}

export function withChange(state: TicketsState, change: Change): TicketsState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: applyChange(state.items, change) };
}
