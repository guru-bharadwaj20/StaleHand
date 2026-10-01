// Inbox app as a pure state machine: list -> open mail -> compose (forward or reply) -> sent.
// Rendering lives in render.ts; this file has no DOM access so it can be tested in Node.
import type { ActionEvent } from "../core/log.js";
import { applyChange } from "../core/changes.js";
import type { Change, Item } from "../core/types.js";

export type View =
  | { name: "list" }
  | { name: "open"; id: string }
  | { name: "compose"; mode: "forward" | "reply"; id: string; to: string; body: string }
  | { name: "sent"; mode: "forward" | "reply"; id: string; to: string };

export interface InboxState {
  items: Item[];
  view: View;
  banner: string | null;
}

export type InboxAction =
  | { type: "open"; id: string }
  | { type: "back" }
  | { type: "forward" }
  | { type: "reply" }
  | { type: "setTo"; text: string }
  | { type: "setBody"; text: string }
  | { type: "send" };

export interface Step {
  state: InboxState;
  events: ActionEvent[];
}

export const initial = (items: Item[]): InboxState => ({ items, view: { name: "list" }, banner: null });

const invalid = (state: InboxState, reason: string): Step => ({ state, events: [{ kind: "invalid", detail: { reason } }] });

export function reduce(state: InboxState, action: InboxAction): Step {
  const v = state.view;
  switch (action.type) {
    case "open":
      if (!state.items.some((i) => i.id === action.id)) return invalid(state, `no mail ${action.id}`);
      return { state: { ...state, view: { name: "open", id: action.id } }, events: [{ kind: "open", itemId: action.id }] };
    case "back":
      return { state: { ...state, view: { name: "list" } }, events: [{ kind: "back" }] };
    case "forward":
    case "reply": {
      if (v.name !== "open") return invalid(state, `${action.type} needs an open mail`);
      const to = action.type === "reply" ? String(state.items.find((i) => i.id === v.id)?.attrs.sender ?? "") : "";
      return {
        state: { ...state, view: { name: "compose", mode: action.type, id: v.id, to, body: "" } },
        events: [{ kind: action.type, itemId: v.id }],
      };
    }
    case "setTo":
    case "setBody": {
      if (v.name !== "compose") return invalid(state, "typing needs the compose view");
      const view = action.type === "setTo" ? { ...v, to: action.text } : { ...v, body: action.text };
      return { state: { ...state, view }, events: [{ kind: action.type, itemId: v.id, detail: { text: action.text } }] };
    }
    case "send": {
      if (v.name !== "compose") return invalid(state, "send needs the compose view");
      if (!v.to.trim()) return { state, events: [{ kind: "send_refused", itemId: v.id, detail: { reason: "no recipient" } }] };
      const detail: Record<string, unknown> = { mode: v.mode, to: v.to };
      if (v.body) detail.body = v.body;
      return {
        state: { ...state, view: { name: "sent", mode: v.mode, id: v.id, to: v.to } },
        events: [{ kind: "send", itemId: v.id, commit: true, detail }],
      };
    }
  }
}

export function withChange(state: InboxState, change: Change): InboxState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: applyChange(state.items, change) };
}
