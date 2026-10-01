# Model serving on the RTX 4500 Ada

Guru's workstation serves models over vLLM's OpenAI-compatible API; experiments use the `openai` backend
(`stalehand.models.registry.load(name, backend="openai", base_url=...)`).

```bash
scripts/ada/setup.sh                                   # once: venv with pinned vLLM
scripts/ada/download.sh qwen3-vl-8b ui-tars-1.5-7b     # weights; revisions appended to runs/ada/revisions.txt
scripts/ada/pair.sh qwen3-vl-8b ui-tars-1.5-7b         # planner on :8000, executor on :8001
scripts/ada/stop.sh
```

- The card has 24 GB. Planner and executor fit together only in fp8 (`QUANT=fp8`, the default); serve a single
  model in bf16 with `QUANT=none scripts/ada/serve.sh NAME 8000`. Record the quantization in each run's
  `config.json`, because Vivian's 4090 runs and these must not be compared as if they used the same weights.
- `DRY_RUN=1 scripts/ada/serve.sh NAME PORT` prints the vLLM command without starting it.
- Logs and pid files go to `runs/ada/` (ignored by git).
