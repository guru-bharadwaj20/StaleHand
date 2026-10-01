// DOM rendering for the shop. Listings carry data-item-id; buttons carry data-role.
import { button, el } from "../core/dom.js";
import { rupees } from "../core/format.js";
import type { Store } from "../core/store.js";
import type { Item } from "../core/types.js";
import type { ShopAction, ShopState } from "./state.js";

const num = (item: Item, key: string) => Number(item.attrs[key] ?? 0);
const str = (item: Item, key: string) => String(item.attrs[key] ?? "");

function stars(rating: number): string {
  const full = Math.floor(rating);
  return "★".repeat(full) + "☆".repeat(5 - full);
}

function ratingLine(item: Item): HTMLElement {
  const r = el("div", { class: "rt" });
  r.append(el("span", { class: "st" }, stars(num(item, "rating"))), ` ${num(item, "rating").toFixed(1)} `,
    el("span", { class: "rv" }, `(${num(item, "reviews").toLocaleString("en-IN")})`));
  return r;
}

function listing(item: Item, onOpen: () => void): HTMLElement {
  const row = el("div", { class: "row", "data-role": "listing", "data-item-id": item.id });
  const name = el("div", { class: "nm" });
  name.append(el("b", {}, str(item, "name")), el("span", {}, ` ${str(item, "category")}`));
  row.append(el("div", { class: "th" }, str(item, "name").slice(0, 2)), name, ratingLine(item),
    el("div", { class: "pr" }, rupees(num(item, "price"))));
  row.addEventListener("click", onOpen);
  return row;
}

function category(state: ShopState): string {
  return str(state.items[0] ?? { id: "", attrs: {} }, "category");
}

function mainView(state: ShopState, go: (a: ShopAction) => void): HTMLElement {
  const main = el("main", { class: "main" });
  if (state.banner) main.append(el("div", { class: "banner", "data-role": "banner" }, "Festive sale: extra 10% off with UPI"));
  const v = state.view;
  if (v.name === "list") {
    main.append(el("div", { class: "bar" }, `Results for "${category(state)}", sorted by relevance`));
    const list = el("div", { class: "list", "data-role": "results" });
    state.items.forEach((it) => list.append(listing(it, () => go({ type: "open", id: it.id }))));
    main.append(list);
    return main;
  }
  const item = state.items.find((i) => i.id === v.id);
  const page = el("section", { class: "page", "data-item-id": v.id });
  page.append(button("back", "← Back to results", () => go({ type: "back" })));
  if (!item) {
    page.append(el("div", { class: "gone", "data-role": "unavailable" }, "This item is currently unavailable."));
  } else {
    page.append(el("h1", { "data-role": "product-name" }, `${str(item, "name")} ${str(item, "category")}`), ratingLine(item),
      el("div", { class: "big", "data-role": "price" }, rupees(num(item, "price"))));
    if (v.name === "product") page.append(button("add-to-cart", "Add to cart", () => go({ type: "add" })));
    else page.append(el("div", { class: "toast", "data-role": "added" }, "Added to cart"));
  }
  main.append(page);
  return main;
}

export function mount(root: HTMLElement, store: Store<ShopState, ShopAction>): void {
  const draw = () => {
    root.replaceChildren();
    const top = el("header", { class: "top" });
    top.append(el("div", { class: "logo" }, "ShopMart"), el("div", { class: "search" }, category(store.state)),
      el("div", { class: "cart", "data-role": "cart" }, `Cart (${store.state.cart.length})`));
    const side = el("nav", { class: "side" });
    side.append(el("b", {}, "Filters"), el("div", {}, "Price"), el("div", {}, "Customer rating"), el("div", {}, "Brand"),
      el("b", {}, "Sort"), el("div", {}, "Relevance"));
    root.append(top, side, mainView(store.state, (a) => store.dispatch(a)));
  };
  store.subscribe(draw);
  draw();
}
