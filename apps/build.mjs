// Bundles each app into one self-contained HTML file: dist/<app>.html (no network needed at run time).
import { build } from "esbuild";
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";

// every directory under src/ with a main.ts is an app, so adding a domain needs no change here
const APPS = readdirSync("src").filter((a) => existsSync(`src/${a}/main.ts`));
mkdirSync("dist", { recursive: true });
for (const app of APPS) {
  const out = await build({ entryPoints: [`src/${app}/main.ts`], bundle: true, format: "iife", target: "es2020",
    minify: false, write: false });
  const js = out.outputFiles[0].text;
  const css = readFileSync(`src/${app}/style.css`, "utf8");
  const html = `<!doctype html><html><head><meta charset="utf-8"><title>${app}</title><style>${css}</style></head>` +
    `<body></body><script>${js}</script></html>`;
  writeFileSync(`dist/${app}.html`, html);
  console.log(`dist/${app}.html ${html.length} bytes`);
}
