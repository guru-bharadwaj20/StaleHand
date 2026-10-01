import { install } from "../core/harness.js";
import { Store } from "../core/store.js";
import { initial, reduce, withChange } from "./state.js";
import { mount } from "./render.js";

install((items) => new Store(initial(items), reduce, withChange), mount);
