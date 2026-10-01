// Bundles the explorer into one self-contained file, dist/index.html, with the result schema built in.
import { build } from "esbuild";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";

const schema = readFileSync("../schema/result.schema.json", "utf8");
const out = await build({ entryPoints: ["src/main.ts"], bundle: true, format: "iife", target: "es2020", minify: true,
  write: false, define: { RESULT_SCHEMA: schema } });
const css = readFileSync("src/style.css", "utf8");
mkdirSync("dist", { recursive: true });
const html = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">` +
  `<title>StaleHand results</title><style>${css}</style></head><body><script>${out.outputFiles[0].text}</script></body></html>`;
writeFileSync("dist/index.html", html);
console.log(`dist/index.html ${html.length} bytes`);
