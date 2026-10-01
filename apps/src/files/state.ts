// Files app as a pure state machine: file list -> file details -> share dialog -> shared.
import { applyChange } from "../core/changes.js";
import type { ActionEvent } from "../core/log.js";
import type { Change, Item } from "../core/types.js";

export type View =
  | { name: "list" }
  | { name: "details"; id: string }
  | { name: "share"; id: string; to: string }
  | { name: "shared"; id: string; to: string };

export interface FilesState {
  items: Item[];
  view: View;
  banner: string | null;
}

export type FilesAction =
  | { type: "open"; id: string }
  | { type: "back" }
  | { type: "share" }
  | { type: "setTo"; text: string }
  | { type: "send" };

export interface Step {
  state: FilesState;
  events: ActionEvent[];
}

export const initial = (items: Item[]): FilesState => ({ items, view: { name: "list" }, banner: null });

const invalid = (state: FilesState, reason: string): Step => ({ state, events: [{ kind: "invalid", detail: { reason } }] });

export function reduce(state: FilesState, action: FilesAction): Step {
  const v = state.view;
  switch (action.type) {
    case "open":
      if (!state.items.some((i) => i.id === action.id)) return invalid(state, `no file ${action.id}`);
      return { state: { ...state, view: { name: "details", id: action.id } }, events: [{ kind: "open", itemId: action.id }] };
    case "back":
      return { state: { ...state, view: { name: "list" } }, events: [{ kind: "back" }] };
    case "share":
      if (v.name !== "details") return invalid(state, "share needs an open file");
      return { state: { ...state, view: { name: "share", id: v.id, to: "" } }, events: [{ kind: "share_dialog", itemId: v.id }] };
    case "setTo":
      if (v.name !== "share") return invalid(state, "typing needs the share dialog");
      return { state: { ...state, view: { ...v, to: action.text } }, events: [{ kind: "setTo", itemId: v.id, detail: { text: action.text } }] };
    case "send": {
      if (v.name !== "share") return invalid(state, "send needs the share dialog");
      if (!v.to.trim()) return { state, events: [{ kind: "share_refused", itemId: v.id, detail: { reason: "no recipient" } }] };
      if (!state.items.some((i) => i.id === v.id)) {
        return { state, events: [{ kind: "share_refused", itemId: v.id, detail: { reason: "file gone" } }] };
      }
      return {
        state: { ...state, view: { name: "shared", id: v.id, to: v.to } },
        events: [{ kind: "share", itemId: v.id, commit: true, detail: { to: v.to } }],
      };
    }
  }
}

export function withChange(state: FilesState, change: Change): FilesState {
  if (change.type === "cosmetic") return { ...state, banner: change.label };
  return { ...state, items: applyChange(state.items, change) };
}
