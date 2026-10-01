// Chat app as a pure state machine: channel -> reply to a message -> sent.
import { applyChange } from "../core/changes.js";
import type { ActionEvent } from "../core/log.js";
import type { Change, Item } from "../core/types.js";

export type View =
  | { name: "channel" }
  | { name: "reply"; id: string; body: string }
  | { name: "sent"; id: string };

export interface ChatState {
  items: Item[];
  view: View;
  banner: string | null;
}

export type ChatAction =
  | { type: "open"; id: string }
  | { type: "back" }
  | { type: "setBody"; text: string }
  | { type: "send" };

export interface Step {
  state: ChatState;
  events: ActionEvent[];
}

export const initial = (items: Item[]): ChatState => ({ items, view: { name: "channel" }, banner: null });

const invalid = (state: ChatState, reason: string): Step => ({ state, events: [{ kind: "invalid", detail: { reason } }] });

export function reduce(state: ChatState, action: ChatAction): Step {
  const v = state.view;
  switch (action.type) {
    case "open":
      if (!state.items.some((i) => i.id === action.id)) return invalid(state, `no message ${action.id}`);
      return { state: { ...state, view: { name: "reply", id: action.id, body: "" } }, events: [{ kind: "open", itemId: action.id }] };
    case "back":
      return { state: { ...state, view: { name: "channel" } }, events: [{ kind: "back" }] };
    case "setBody":
      if (v.name !== "reply") return invalid(state, "typing needs a reply box");
      return { state: { ...state, view: { ...v, body: action.text } }, events: [{ kind: "setBody", itemId: v.id, detail: { text: action.text } }] };
    case "send": {
      if (v.name !== "reply") return invalid(state, "send needs a reply box");
      if (!v.body.trim()) return { state, events: [{ kind: "send_refused", itemId: v.id, detail: { reason: "empty reply" } }] };
      return {
        state: { ...state, view: { name: "sent", id: v.id } },
        events: [{ kind: "send", itemId: v.id, commit: true, detail: { mode: "reply", body: v.body } }],
      };
    }
  }
}

export function withChange(state: ChatState, change: Change): ChatState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: applyChange(state.items, change) };
}
