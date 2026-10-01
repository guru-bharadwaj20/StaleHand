"""Token cost of each episode, recounted from the trajectories.

Trajectories log every model reply, so output tokens are counted exactly by re-encoding the reply with the model's
own tokenizer. Every call also sends one screenshot at the fixed 1288x728 viewport; its token count is the same on
every call to a model and is measured once with that model's image processor. Prompt text was not logged, so input
text tokens are not counted.

usage: python tokens.py report tokens/*.jsonl > tokens_report.md
       python tokens.py --model Qwen/Qwen3-VL-8B-Instruct=/path/to/snapshot \
           --model ByteDance-Seed/UI-TARS-1.5-7B=/path/to/snapshot --out tokens.jsonl RUN_SET_DIR...
"""
import argparse
import json
from pathlib import Path

VIEWPORT = (1288, 728)


def image_tokens(path: str) -> int:
    from PIL import Image
    from transformers import AutoImageProcessor
    proc = AutoImageProcessor.from_pretrained(path, use_fast=False)  # the fast one needs torch
    grid = proc(images=[Image.new("RGB", VIEWPORT, "white")], return_tensors="np")["image_grid_thw"][0]
    return int(grid[0] * grid[1] * grid[2]) // proc.merge_size ** 2


def report(paths) -> str:
    """Mean tokens per episode, per run set and guard."""
    groups = {}
    for path in paths:
        for line in open(path):
            r = json.loads(line)
            groups.setdefault((r["run_set"], r["architecture"], r["guard"]), []).append(r)
    mean = lambda rs, f: f"{sum(map(f, rs)) / len(rs):,.0f}"
    lines = ["Mean tokens per episode, recounted from the logged replies (output) and the screenshot sent with every "
             "call (image). Prompt text was not logged and is not counted.", "",
             "| run set | architecture | guard | episodes | planner output | executor output | checker output | "
             "image input |", "|---|---|---|---|---|---|---|---|"]
    for (run_set, arch, guard), rs in groups.items():
        out = lambda role: mean(rs, lambda r: r["output_tokens"].get(role, 0))
        lines.append(f"| {run_set} | {arch} | {guard} | {len(rs)} | {out('planner')} | {out('executor')} | "
                     f"{out('checker')} | {mean(rs, lambda r: sum(r['image_tokens'].values()))} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    import sys
    if sys.argv[1:2] == ["report"]:
        print(report(sys.argv[2:]), end="")
        return 0
    p = argparse.ArgumentParser()
    p.add_argument("--model", action="append", required=True, help="HF id=local snapshot directory")
    p.add_argument("--out", required=True)
    p.add_argument("runs", nargs="+")
    a = p.parse_args()
    from transformers import AutoTokenizer
    paths = dict(m.split("=", 1) for m in a.model)
    toks = {name: AutoTokenizer.from_pretrained(path) for name, path in paths.items()}
    images = {name: image_tokens(path) for name, path in paths.items()}
    with open(a.out, "w") as f:
        for run_set in a.runs:
            for traj_path in sorted(Path(run_set).glob("*/trajectories/*.json")):
                t = json.loads(traj_path.read_text())
                row = {"run_set": Path(run_set).name, "job": traj_path.parent.parent.name,
                       "scenario_id": t["scenario_id"], "architecture": t["architecture"], "guard": t["guard"],
                       "calls": {}, "output_tokens": {}, "image_tokens": {}}
                for e in t["entries"]:
                    if e["kind"] != "model_call":
                        continue
                    role, model = e["role"], e["model"]
                    n = len(toks[model].encode(e["output"], add_special_tokens=False))
                    row["calls"][role] = row["calls"].get(role, 0) + 1
                    row["output_tokens"][role] = row["output_tokens"].get(role, 0) + n
                    row["image_tokens"][role] = row["image_tokens"].get(role, 0) + images[model]
                f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps({"image_tokens_per_call": images}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
