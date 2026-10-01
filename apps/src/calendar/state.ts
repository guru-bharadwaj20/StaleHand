// Calendar app as a pure state machine: agenda -> meeting details -> joined.
import { applyChange } from "../core/changes.js";
import type { ActionEvent } from "../core/log.js";
import type { Change, Item } from "../core/types.js";

export type View = { name: "agenda" } | { name: "meeting"; id: string } | { name: "joined"; id: string };

export interface CalendarState {
  items: Item[];
  view: View;
  banner: string | null;
}

export type CalendarAction = { type: "open"; id: string } | { type: "back" } | { type: "join" };

export const initial = (items: Item[]): CalendarState => ({ items, view: { name: "agenda" }, banner: null });

export function reduce(state: CalendarState, action: CalendarAction): { state: CalendarState; events: ActionEvent[] } {
  const v = state.view;
  switch (action.type) {
    case "open":
      if (!state.items.some((i) => i.id === action.id)) {
        return { state, events: [{ kind: "invalid", detail: { reason: `no meeting ${action.id}` } }] };
      }
      return { state: { ...state, view: { name: "meeting", id: action.id } }, events: [{ kind: "open", itemId: action.id }] };
    case "back":
      return { state: { ...state, view: { name: "agenda" } }, events: [{ kind: "back" }] };
    case "join": {
      if (v.name !== "meeting") return { state, events: [{ kind: "invalid", detail: { reason: "join needs a meeting" } }] };
      const m = state.items.find((i) => i.id === v.id);
      if (!m) return { state, events: [{ kind: "join_refused", itemId: v.id, detail: { reason: "cancelled" } }] };
      return {
        state: { ...state, view: { name: "joined", id: v.id } },
        events: [{ kind: "join", itemId: v.id, commit: true, detail: { start: m.attrs.start } }],
      };
    }
  }
}

// keeps the agenda in time order, as a real calendar would after a reschedule or an added meeting
const byStart = (items: Item[]) => [...items].sort((a, b) => Number(a.attrs.start ?? 0) - Number(b.attrs.start ?? 0));

export function withChange(state: CalendarState, change: Change): CalendarState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: byStart(applyChange(state.items, change)) };
}
