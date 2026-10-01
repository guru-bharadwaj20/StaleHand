// DOM rendering for the chat. Messages show oldest at the top and carry data-item-id; controls carry data-role.
import { button, el } from "../core/dom.js";
import { formatTime, initials } from "../core/format.js";
import type { Store } from "../core/store.js";
import type { Item } from "../core/types.js";
import type { ChatAction, ChatState } from "./state.js";

const CHANNELS = ["# general", "# project-atlas", "# random", "# help-desk", "# design"];

const str = (item: Item, key: string) => String(item.attrs[key] ?? "");
const oldestFirst = (items: Item[]) => [...items].sort((a, b) => Number(a.attrs.sent ?? 0) - Number(b.attrs.sent ?? 0));

function message(item: Item, selected: boolean, onOpen: () => void): HTMLElement {
  const m = el("div", { class: `msg${selected ? " sel" : ""}`, "data-role": "message", "data-item-id": item.id });
  const head = el("div", { class: "hd" });
  head.append(el("b", {}, str(item, "sender")), el("span", { class: "tm" }, formatTime(Number(item.attrs.sent ?? 0))));
  const body = el("div", { class: "bd" });
  body.append(head, el("div", { class: "tx" }, str(item, "text") + (item.attrs.edited ? " (edited)" : "")));
  m.append(el("div", { class: "av" }, initials(str(item, "sender"))), body);
  m.addEventListener("click", onOpen);
  return m;
}

function mainView(state: ChatState, go: (a: ChatAction) => void, keep: (n: HTMLElement) => void): HTMLElement {
  const main = el("main", { class: "main" });
  main.append(el("div", { class: "bar" }, "# project-atlas"));
  if (state.banner) main.append(el("div", { class: "banner", "data-role": "banner" }, "New messages below"));
  const v = state.view;
  const sel = v.name === "channel" ? null : v.id;
  const list = el("div", { class: "list", "data-role": "messages" });
  oldestFirst(state.items).forEach((it) => list.append(message(it, it.id === sel, () => go({ type: "open", id: it.id }))));
  main.append(list);
  keep(list);
  const foot = el("div", { class: "foot" });
  if (v.name === "reply") {
    const target = state.items.find((i) => i.id === v.id);
    const body = el("textarea", { "data-role": "body", placeholder: "Write a reply" }) as HTMLTextAreaElement;
    body.value = v.body;
    body.addEventListener("input", () => go({ type: "setBody", text: body.value }));
    foot.append(el("div", { class: "re" }, `Replying to ${target ? str(target, "sender") : "a deleted message"}`), body,
      button("send", "Send", () => go({ type: "send" })), button("back", "Cancel", () => go({ type: "back" })));
  } else if (v.name === "sent") {
    foot.append(el("div", { class: "toast", "data-role": "sent" }, "Reply sent"));
  } else {
    foot.append(el("div", { class: "hint" }, "Click a message to reply"));
  }
  main.append(foot);
  return main;
}

export function mount(root: HTMLElement, store: Store<ChatState, ChatAction>): void {
  const draw = () => {
    root.replaceChildren();
    const side = el("nav", { class: "side" });
    side.append(el("div", { class: "ws" }, "Atlas team"));
    CHANNELS.forEach((c) => side.append(el("div", { class: `f${c === "# project-atlas" ? " on" : ""}` }, c)));
    // newest messages sit at the bottom, so scroll there like a real chat
    root.append(side, mainView(store.state, (a) => store.dispatch(a), (list) => queueMicrotask(() => { list.scrollTop = list.scrollHeight; })));
  };
  // typing must not rebuild the DOM, or the textarea loses focus mid-word
  store.subscribe((_s, cause) => { if (cause !== "setBody") draw(); });
  draw();
}
