// DOM rendering for the tickets app. Ticket rows carry data-item-id; buttons and inputs carry data-role.
import { button, el } from "../core/dom.js";
import { formatTime } from "../core/format.js";
import type { Store } from "../core/store.js";
import type { Item } from "../core/types.js";
import type { TicketsAction, TicketsState } from "./state.js";

const QUEUES = ["All open", "Unassigned", "My tickets", "Recently updated", "Closed"];

const str = (item: Item, key: string) => String(item.attrs[key] ?? "");

function priority(item: Item): HTMLElement {
  const p = str(item, "priority");
  return el("span", { class: `pri ${p}` }, p.charAt(0).toUpperCase() + p.slice(1));
}

function row(item: Item, onOpen: () => void): HTMLElement {
  const r = el("div", { class: "row", "data-role": "ticket-row", "data-item-id": item.id });
  const pri = el("div", { class: "pc" });
  pri.append(priority(item));
  r.append(el("div", { class: "key" }, str(item, "key")), el("div", { class: "ti" }, str(item, "title")), pri,
    el("div", { class: "rp" }, str(item, "reporter")), el("div", { class: "as" }, str(item, "assignee") || "Unassigned"),
    el("div", { class: "tm" }, formatTime(Number(item.attrs.created ?? 0))));
  r.addEventListener("click", onOpen);
  return r;
}

function header(): HTMLElement {
  const h = el("div", { class: "row head" });
  h.append(el("div", { class: "key" }, "Key"), el("div", { class: "ti" }, "Summary"), el("div", { class: "pc" }, "Priority"),
    el("div", { class: "rp" }, "Reporter"), el("div", { class: "as" }, "Assignee"), el("div", { class: "tm" }, "Created"));
  return h;
}

function mainView(state: TicketsState, go: (a: TicketsAction) => void): HTMLElement {
  const main = el("main", { class: "main" });
  if (state.banner) main.append(el("div", { class: "banner", "data-role": "banner" }, "Scheduled maintenance tonight at 11 PM."));
  const v = state.view;
  if (v.name === "list") {
    main.append(el("div", { class: "bar" }, "All open tickets, newest first"), header());
    const list = el("div", { class: "list", "data-role": "ticket-list" });
    state.items.forEach((it) => list.append(row(it, () => go({ type: "open", id: it.id }))));
    main.append(list);
    return main;
  }
  const t = state.items.find((i) => i.id === v.id);
  const pane = el("section", { class: "pane", "data-item-id": v.id });
  pane.append(button("back", "← Back to queue", () => go({ type: "back" })));
  if (!t) {
    pane.append(el("div", { class: "gone", "data-role": "unavailable" }, "This ticket has been closed."));
    main.append(pane);
    return main;
  }
  const meta = el("div", { class: "meta" });
  meta.append(priority(t), ` reported by ${str(t, "reporter")} at ${formatTime(Number(t.attrs.created ?? 0))} · ${str(t, "assignee") || "Unassigned"}`);
  pane.append(el("h1", { "data-role": "ticket-title" }, `${str(t, "key")}  ${str(t, "title")}`), meta);
  if (v.name === "ticket") {
    pane.append(button("assign", "Assign", () => go({ type: "assign" })));
  } else if (v.name === "assign") {
    const to = el("input", { "data-role": "to", placeholder: "Assignee name", value: v.to, autocomplete: "off" }) as HTMLInputElement;
    to.addEventListener("input", () => go({ type: "setTo", text: to.value }));
    pane.append(el("div", { class: "mode" }, `Assign ${str(t, "key")}`), to, button("save", "Save", () => go({ type: "save" })));
  } else {
    pane.append(el("div", { class: "toast", "data-role": "assigned" }, `Assigned to ${v.to}`));
  }
  main.append(pane);
  return main;
}

export function mount(root: HTMLElement, store: Store<TicketsState, TicketsAction>): void {
  const draw = () => {
    root.replaceChildren();
    const top = el("header", { class: "top" });
    top.append(el("div", { class: "logo" }, "Helpdesk"), el("div", { class: "search" }, "Search tickets"));
    const side = el("nav", { class: "side" });
    QUEUES.forEach((q) => side.append(el("div", { class: `f${q === "All open" ? " on" : ""}` }, q)));
    root.append(top, side, mainView(store.state, (a) => store.dispatch(a)));
  };
  // typing must not rebuild the DOM, or the input loses focus mid-word
  store.subscribe((_s, cause) => { if (cause !== "setTo") draw(); });
  draw();
}
