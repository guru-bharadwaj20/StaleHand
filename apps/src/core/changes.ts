// Applies change events to item lists; mirrors src/stalehand/scenarios/changes.py.
import type { Change, Item } from "./types.js";

export function applyChange(items: readonly Item[], change: Change): Item[] {
  const list = [...items];
  const has = new Set(list.map((i) => i.id));
  switch (change.type) {
    case "insert": {
      const clash = change.items.filter((i) => has.has(i.id)).map((i) => i.id);
      if (clash.length) throw new Error(`insert would duplicate ids ${clash.join(",")}`);
      list.splice(change.position, 0, ...change.items);
      return list;
    }
    case "remove": {
      const missing = change.ids.filter((id) => !has.has(id));
      if (missing.length) throw new Error(`cannot remove missing ids ${missing.join(",")}`);
      return list.filter((i) => !change.ids.includes(i.id));
    }
    case "update": {
      if (!has.has(change.id)) throw new Error(`cannot update missing id ${change.id}`);
      return list.map((i) => (i.id === change.id ? { id: i.id, attrs: { ...i.attrs, ...change.attrs } } : i));
    }
    case "sort": {
      const key = change.field;
      const withValue = list.filter((i) => i.attrs[key] !== undefined && i.attrs[key] !== null);
      const without = list.filter((i) => i.attrs[key] === undefined || i.attrs[key] === null);
      const sign = change.descending ? -1 : 1;
      withValue.sort((a, b) => sign * ((a.attrs[key] as number) < (b.attrs[key] as number) ? -1 : (a.attrs[key] as number) > (b.attrs[key] as number) ? 1 : 0));
      return [...withValue, ...without];
    }
    case "cosmetic":
      return list;
  }
}
