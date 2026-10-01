// DOM rendering for the files app. File rows carry data-item-id; buttons and inputs carry data-role.
import { button, el } from "../core/dom.js";
import { formatTime } from "../core/format.js";
import type { Store } from "../core/store.js";
import type { Item } from "../core/types.js";
import type { FilesAction, FilesState } from "./state.js";

const PLACES = ["My Drive", "Shared with me", "Recent", "Starred", "Trash"];
const ICONS: Record<string, string> = { report: "PDF", invoice: "PDF", slides: "PPT", spreadsheet: "XLS", contract: "DOC" };

const str = (item: Item, key: string) => String(item.attrs[key] ?? "");

function size(kb: number): string {
  return kb >= 1024 ? `${(kb / 1024).toFixed(1)} MB` : `${kb} KB`;
}

function row(item: Item, onOpen: () => void): HTMLElement {
  const r = el("div", { class: "row", "data-role": "file-row", "data-item-id": item.id });
  r.append(el("div", { class: `ic ${str(item, "type")}` }, ICONS[str(item, "type")] ?? "FILE"),
    el("div", { class: "nm" }, str(item, "name")), el("div", { class: "ow" }, str(item, "owner")),
    el("div", { class: "tm" }, formatTime(Number(item.attrs.modified ?? 0))),
    el("div", { class: "sz" }, size(Number(item.attrs.size_kb ?? 0))));
  r.addEventListener("click", onOpen);
  return r;
}

function header(): HTMLElement {
  const h = el("div", { class: "row head" });
  h.append(el("div", { class: "ic" }), el("div", { class: "nm" }, "Name"), el("div", { class: "ow" }, "Owner"),
    el("div", { class: "tm" }, "Last modified"), el("div", { class: "sz" }, "File size"));
  return h;
}

function mainView(state: FilesState, go: (a: FilesAction) => void): HTMLElement {
  const main = el("main", { class: "main" });
  if (state.banner) main.append(el("div", { class: "banner", "data-role": "banner" }, "You've used 94% of your storage."));
  const v = state.view;
  if (v.name === "list") {
    main.append(el("div", { class: "bar" }, "Recent files"), header());
    const list = el("div", { class: "list", "data-role": "file-list" });
    state.items.forEach((it) => list.append(row(it, () => go({ type: "open", id: it.id }))));
    main.append(list);
    return main;
  }
  const file = state.items.find((i) => i.id === v.id);
  const pane = el("section", { class: "pane", "data-item-id": v.id });
  pane.append(button("back", "← Back to files", () => go({ type: "back" })));
  if (!file) {
    pane.append(el("div", { class: "gone", "data-role": "unavailable" }, "This file is no longer available."));
    main.append(pane);
    return main;
  }
  pane.append(el("h1", { "data-role": "file-name" }, str(file, "name")),
    el("div", { class: "meta" }, `${str(file, "owner")} · modified ${formatTime(Number(file.attrs.modified ?? 0))} · ${size(Number(file.attrs.size_kb ?? 0))}`));
  if (v.name === "details") {
    pane.append(button("share", "Share", () => go({ type: "share" })));
  } else if (v.name === "share") {
    const to = el("input", { "data-role": "to", placeholder: "Add people by email", value: v.to, autocomplete: "off" }) as HTMLInputElement;
    to.addEventListener("input", () => go({ type: "setTo", text: to.value }));
    pane.append(el("div", { class: "mode" }, `Share "${str(file, "name")}"`), to, button("send", "Send", () => go({ type: "send" })));
  } else {
    pane.append(el("div", { class: "toast", "data-role": "shared" }, `Shared with ${v.to}`));
  }
  main.append(pane);
  return main;
}

export function mount(root: HTMLElement, store: Store<FilesState, FilesAction>): void {
  const draw = () => {
    root.replaceChildren();
    const top = el("header", { class: "top" });
    top.append(el("div", { class: "logo" }, "Drive"), el("div", { class: "search" }, "Search in Drive"));
    const side = el("nav", { class: "side" });
    side.append(el("div", { class: "new" }, "+ New"));
    PLACES.forEach((p) => side.append(el("div", { class: `f${p === "Recent" ? " on" : ""}` }, p)));
    root.append(top, side, mainView(store.state, (a) => store.dispatch(a)));
  };
  // typing must not rebuild the DOM, or the input loses focus mid-word
  store.subscribe((_s, cause) => { if (cause !== "setTo") draw(); });
  draw();
}
