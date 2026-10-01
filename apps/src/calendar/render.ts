// DOM rendering for the calendar. Agenda entries carry data-item-id; buttons carry data-role.
import { button, el } from "../core/dom.js";
import { formatTime, initials } from "../core/format.js";
import type { Store } from "../core/store.js";
import type { Item } from "../core/types.js";
import type { CalendarAction, CalendarState } from "./state.js";

const CALENDARS = ["My calendar", "Team", "Holidays", "Birthdays"];

const str = (item: Item, key: string) => String(item.attrs[key] ?? "");

function span(item: Item): string {
  const start = Number(item.attrs.start ?? 0);
  return `${formatTime(start)} – ${formatTime(start + Number(item.attrs.minutes ?? 0))}`;
}

function entry(item: Item, onOpen: () => void): HTMLElement {
  const r = el("div", { class: "row", "data-role": "meeting-row", "data-item-id": item.id });
  r.append(el("div", { class: "tm" }, span(item)), el("div", { class: "dot" }), el("div", { class: "ti" }, str(item, "title")),
    el("div", { class: "av" }, initials(str(item, "with"))), el("div", { class: "wh" }, str(item, "with")));
  r.addEventListener("click", onOpen);
  return r;
}

function mainView(state: CalendarState, go: (a: CalendarAction) => void): HTMLElement {
  const main = el("main", { class: "main" });
  if (state.banner) main.append(el("div", { class: "banner", "data-role": "banner" }, "Reminder: update your working hours for next week."));
  const v = state.view;
  if (v.name === "agenda") {
    main.append(el("div", { class: "bar" }, "Today · upcoming"));
    const list = el("div", { class: "list", "data-role": "agenda" });
    state.items.forEach((it) => list.append(entry(it, () => go({ type: "open", id: it.id }))));
    main.append(list);
    return main;
  }
  const m = state.items.find((i) => i.id === v.id);
  const pane = el("section", { class: "pane", "data-item-id": v.id });
  pane.append(button("back", "← Back to agenda", () => go({ type: "back" })));
  if (!m) {
    pane.append(el("div", { class: "gone", "data-role": "unavailable" }, "This meeting was cancelled."));
  } else {
    pane.append(el("h1", { "data-role": "meeting-title" }, str(m, "title")),
      el("div", { class: "meta" }, `${span(m)} · with ${str(m, "with")}`));
    if (v.name === "meeting") pane.append(button("join", "Join video call", () => go({ type: "join" })));
    else pane.append(el("div", { class: "toast", "data-role": "joined" }, `You joined ${str(m, "title")}`));
  }
  main.append(pane);
  return main;
}

export function mount(root: HTMLElement, store: Store<CalendarState, CalendarAction>): void {
  const draw = () => {
    root.replaceChildren();
    const top = el("header", { class: "top" });
    top.append(el("div", { class: "logo" }, "Calendar"), el("div", { class: "today" }, "Today"));
    const side = el("nav", { class: "side" });
    side.append(el("div", { class: "new" }, "+ Create"));
    CALENDARS.forEach((c) => side.append(el("div", { class: "f" }, c)));
    root.append(top, side, mainView(store.state, (a) => store.dispatch(a)));
  };
  store.subscribe(draw);
  draw();
}
