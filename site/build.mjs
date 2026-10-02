// Bundles the explorer into one self-contained file, dist/index.html, with the result schema built in.
import { build } from "esbuild";
import { existsSync, mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

// Every run set under ../results/<machine>/<set>/<job>/results.jsonl is built in, so a rebuild after a run lands
// is all it takes to browse it. Keys are "<machine>/<set>".
function resultSets(root) {
  const sets = {};
  const dirs = (d) => (existsSync(d) ? readdirSync(d, { withFileTypes: true }).filter((e) => e.isDirectory()).map((e) => e.name).sort() : []);
  for (const machine of dirs(root)) for (const set of dirs(join(root, machine))) {
    const parts = dirs(join(root, machine, set)).map((job) => join(root, machine, set, job, "results.jsonl"))
      .filter(existsSync).map((f) => readFileSync(f, "utf8").trimEnd());
    if (parts.length) sets[`${machine}/${set}`] = parts.join("\n") + "\n";
  }
  return sets;
}

const schema = readFileSync("../schema/result.schema.json", "utf8");
const sets = process.env.STALEHAND_SITE_NO_RESULTS ? {} : resultSets("../results");
const out = await build({ entryPoints: ["src/main.ts"], bundle: true, format: "iife", target: "es2020", minify: true,
  write: false, define: { RESULT_SCHEMA: schema, RESULT_SETS: JSON.stringify(sets) } });
const css = readFileSync("src/style.css", "utf8");
mkdirSync("dist", { recursive: true });
const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">` +
  `<title>StaleHand results</title><style>${css}</style></head><body><script>${out.outputFiles[0].text}</script></body></html>`;
writeFileSync("dist/index.html", html);
console.log(`dist/index.html ${html.length} bytes, run sets: ${Object.keys(sets).join(", ") || "none"}`);
