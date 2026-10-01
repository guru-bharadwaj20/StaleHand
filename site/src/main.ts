// Results explorer: load result JSONL (file picker, drag and drop, or ?src=<url> when hosted), validate every
// row against schema/result.schema.json, then group and filter. Nothing on the page is typed in by hand.
import { FIELDS, loadJsonl, makeValidator, type Problem, type Result } from "./rows.js";
import { mainCharts } from "./charts.js";
import { OUTCOMES, distinct, filterRows, group, pct } from "./summary.js";

declare const RESULT_SCHEMA: object; // injected by build.mjs from schema/result.schema.json

const validate = makeValidator(RESULT_SCHEMA);
const state = { rows: [] as Result[], problems: [] as Problem[], sources: [] as string[],
                groupBy: ["guard", "change_kind"], filters: {} as Record<string, string> };

function el<K extends keyof HTMLElementTagNameMap>(tag: K, attrs: Record<string, string> = {}, text?: string) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
  if (text !== undefined) node.textContent = text;
  return node;
}

function add(text: string, source: string) {
  const got = loadJsonl(text, source, validate);
  state.rows.push(...got.rows);
  state.problems.push(...got.problems);
  state.sources.push(`${source} (${got.rows.length} rows${got.problems.length ? `, ${got.problems.length} rejected` : ""})`);
  draw();
}

function select(label: string, options: string[], value: string, onChange: (v: string) => void): HTMLElement {
  const wrap = el("label", { class: "pick" });
  const s = el("select");
  for (const o of options) {
    const opt = el("option", { value: o }, o || "(all)");
    if (o === value) opt.selected = true;
    s.append(opt);
  }
  s.addEventListener("change", () => onChange(s.value));
  wrap.append(`${label} `, s);
  return wrap;
}

function controls(): HTMLElement {
  const box = el("section", { class: "controls" });
  const names = Object.keys(FIELDS);
  box.append(el("h2", {}, "Group by"));
  state.groupBy.forEach((g, i) => box.append(select(`level ${i + 1}`, ["", ...names], g, (v) => {
    state.groupBy[i] = v;
    draw();
  })));
  box.append(el("h2", {}, "Filter"));
  for (const f of names) {
    const values = distinct(state.rows, FIELDS[f]!);
    if (values.length > 1) box.append(select(f, ["", ...values], state.filters[f] ?? "", (v) => {
      state.filters[f] = v;
      draw();
    }));
  }
  return box;
}

function table(rows: Result[]): HTMLElement {
  const keys = state.groupBy.filter(Boolean);
  const groups = group(rows, keys.map((k) => FIELDS[k]!));
  const t = el("table", { "data-role": "summary" });
  const head = el("tr");
  [...keys, "n", "success", "stale", ...OUTCOMES.slice(2), "false alarms", "model s/episode"]
    .forEach((h) => head.append(el("th", {}, h)));
  t.append(head);
  for (const g of groups) {
    const tr = el("tr");
    g.key.forEach((k) => tr.append(el("td", {}, k || "–")));
    tr.append(el("td", { class: "num" }, String(g.n)), el("td", { class: "num" }, pct(g.successRate)),
      el("td", { class: "num" }, pct(g.staleRate)));
    OUTCOMES.slice(2).forEach((o) => tr.append(el("td", { class: "num" }, String(g.counts[o] ?? 0))));
    tr.append(el("td", { class: "num" }, String(g.falseAlarms)), el("td", { class: "num" }, g.meanSeconds.toFixed(2)));
    t.append(tr);
  }
  const wrap = el("div", { class: "scroll" });
  wrap.append(t);
  return wrap;
}

function charts(rows: Result[]): HTMLElement {
  const box = el("section", { class: "charts", "aria-label": "Main results per guard" });
  box.innerHTML = mainCharts(rows).join(""); // markup built from escaped text only, see charts.ts
  return box;
}

function problems(): HTMLElement {
  const box = el("details", { class: "problems" });
  box.append(el("summary", {}, `${state.problems.length} rows rejected by the schema`));
  const ul = el("ul");
  state.problems.slice(0, 200).forEach((p) => ul.append(el("li", {}, `${p.source}:${p.line} ${p.message}`)));
  box.append(ul);
  return box;
}

function draw() {
  const main = document.getElementById("app")!;
  main.replaceChildren();
  const files = el("p", { class: "sources" }, state.sources.length ? `Loaded: ${state.sources.join(", ")}` : "No result files loaded yet.");
  main.append(files);
  if (state.problems.length) main.append(problems());
  if (!state.rows.length) return;
  const rows = filterRows(state.rows, FIELDS, state.filters);
  main.append(controls(), el("p", { class: "count" }, `${rows.length} of ${state.rows.length} episodes`), charts(rows), table(rows));
}

function setup() {
  document.body.append(el("header", {}, ""), el("main", { id: "app" }));
  const header = document.querySelector("header")!;
  const input = el("input", { type: "file", accept: ".jsonl,.json", multiple: "" }) as HTMLInputElement;
  input.addEventListener("change", async () => {
    for (const f of input.files ?? []) add(await f.text(), f.name);
    input.value = "";
  });
  header.append(el("h1", {}, "StaleHand results"), input);
  document.addEventListener("dragover", (e) => e.preventDefault());
  document.addEventListener("drop", async (e) => {
    e.preventDefault();
    for (const f of e.dataTransfer?.files ?? []) add(await f.text(), f.name);
  });
  draw();
  for (const src of new URLSearchParams(location.search).getAll("src")) {
    fetch(src).then((r) => (r.ok ? r.text() : Promise.reject(new Error(`${r.status}`))))
      .then((t) => add(t, src))
      .catch((e: Error) => {
        state.problems.push({ source: src, line: 0, message: `could not load: ${e.message}` });
        draw();
      });
  }
}

setup();
