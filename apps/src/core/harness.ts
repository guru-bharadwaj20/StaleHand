// The page-side API the Python environment drives through Playwright: window.stalehand.
import type { LoggedEvent } from "./log.js";
import type { Store } from "./store.js";
import type { Change, Item, Scenario } from "./types.js";

export interface HarnessApi {
  ready: boolean;
  load(scenario: Scenario): void;
  apply(change: Change): void;
  events(): LoggedEvent[];
  view(): unknown;
}

declare global {
  interface Window {
    stalehand: HarnessApi;
  }
}

export function install<S extends { view: unknown }, A extends { type: string }>(
  createStore: (items: Item[]) => Store<S, A>, mount: (root: HTMLElement, store: Store<S, A>) => void,
): void {
  let store: Store<S, A> | null = null;
  const need = () => {
    if (!store) throw new Error("call stalehand.load(scenario) first");
    return store;
  };
  window.stalehand = {
    ready: true,
    load(scenario) {
      store = createStore(scenario.items);
      mount(document.body, store);
    },
    apply: (change) => need().change(change),
    events: () => need().log.events(),
    view: () => need().state.view,
  };
}
