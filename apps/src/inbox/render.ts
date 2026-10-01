// DOM rendering for the inbox. Every clickable thing carries data-role, and mail rows carry data-item-id,
// so the Python side can find ground-truth boxes without guessing from pixels.
import { formatTime, initials } from "../core/format.js";
import type { Store } from "../core/store.js";
import type { Item } from "../core/types.js";
import type { InboxAction, InboxState } from "./state.js";

const FOLDERS = ["Inbox", "Starred", "Snoozed", "Sent", "Drafts", "Archive", "Spam"];

function el<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, string> = {}, text?: string) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

const str = (item: Item, key: string) => String(item.attrs[key] ?? "");

function row(item: Item, onOpen: () => void): HTMLElement {
  const r = el("div", { class: `row${item.attrs.unread ? " unread" : ""}`, "data-role": "mail-row", "data-item-id": item.id });
  r.append(el("div", { class: "av" }, initials(str(item, "sender"))), el("div", { class: "snd" }, str(item, "sender")));
  const sub = el("div", { class: "sub" });
  sub.append(el("b", {}, str(item, "subject")), el("span", {}, ` - ${str(item, "snippet")}`));
  r.append(sub, el("div", { class: "tm" }, formatTime(Number(item.attrs.received ?? 0))));
  r.addEventListener("click", onOpen);
  return r;
}

function button(role: string, label: string, onClick: () => void): HTMLElement {
  const b = el("button", { "data-role": role, type: "button" }, label);
  b.addEventListener("click", onClick);
  return b;
}

function mainView(state: InboxState, go: (a: InboxAction) => void): HTMLElement {
  const main = el("main", { class: "main" });
  if (state.banner) main.append(el("div", { class: "banner", "data-role": "banner" }, "Your storage is 91% full. Free up space to keep receiving mail."));
  const v = state.view;
  if (v.name === "list") {
    main.append(el("div", { class: "bar" }, "Primary"));
    const list = el("div", { class: "list", "data-role": "mail-list" });
    state.items.forEach((it) => list.append(row(it, () => go({ type: "open", id: it.id }))));
    main.append(list);
    return main;
  }
  const mail = state.items.find((i) => i.id === v.id);
  const pane = el("section", { class: "pane", "data-item-id": v.id });
  pane.append(button("back", "← Back to Inbox", () => go({ type: "back" })));
  if (mail) {
    pane.append(el("h1", { "data-role": "subject" }, str(mail, "subject")));
    pane.append(el("div", { class: "from" }, `${str(mail, "sender")} · ${formatTime(Number(mail.attrs.received ?? 0))}`));
    pane.append(el("p", { class: "body" }, str(mail, "snippet")));
  }
  if (v.name === "open") {
    const actions = el("div", { class: "actions" });
    actions.append(button("reply", "Reply", () => go({ type: "reply" })), button("forward", "Forward", () => go({ type: "forward" })));
    pane.append(actions);
  } else if (v.name === "compose") {
    const to = el("input", { "data-role": "to", placeholder: "To", value: v.to, autocomplete: "off" }) as HTMLInputElement;
    to.addEventListener("input", () => go({ type: "setTo", text: to.value }));
    const body = el("textarea", { "data-role": "body", placeholder: "Write your message" }) as HTMLTextAreaElement;
    body.value = v.body;
    body.addEventListener("input", () => go({ type: "setBody", text: body.value }));
    pane.append(el("div", { class: "mode" }, v.mode === "forward" ? "Forward" : "Reply"), to, body, button("send", "Send", () => go({ type: "send" })));
  } else if (v.name === "sent") {
    pane.append(el("div", { class: "toast", "data-role": "sent" }, `Message sent to ${v.to}`));
  }
  main.append(pane);
  return main;
}

export function mount(root: HTMLElement, store: Store<InboxState, InboxAction>): void {
  const go = (a: InboxAction) => store.dispatch(a);
  const draw = () => {
    root.replaceChildren();
    const top = el("header", { class: "top" });
    top.append(el("div", { class: "logo" }, "Mail"), el("div", { class: "search" }, "Search mail"));
    const side = el("nav", { class: "side" });
    side.append(el("div", { class: "compose" }, "Compose"));
    FOLDERS.forEach((f) => side.append(el("div", { class: `f${f === "Inbox" ? " on" : ""}` }, f)));
    root.append(top, side, mainView(store.state, go));
  };
  // typing must not rebuild the DOM, or the input loses focus mid-word
  store.subscribe((_s, cause) => { if (cause !== "setTo" && cause !== "setBody") draw(); });
  draw();
}
