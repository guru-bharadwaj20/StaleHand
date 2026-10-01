# Results explorer

A static page that reads result JSONL, checks every row against `schema/result.schema.json` and shows outcome
rates grouped and filtered by guard, change kind, domain, task kind, variant and executor. Rows that fail the
schema are listed with their file and line, and left out of every table.

```bash
npm ci && npm run build      # dist/index.html, one self-contained file
```

Above the table, inline SVG bar charts show per guard the stale rate on relevant changes, the false-alarm rate on
harmless changes (`none` or `irrelevant`, as in `report/tables.py`) and mean planner calls and model seconds. They are
computed in `src/charts.ts` from the loaded, filtered rows only.

Open `dist/index.html` and pick or drop result files. When served over HTTP next to the results,
`index.html?src=results/guru-4500/main.jsonl` loads files directly (repeat `src` for several).
