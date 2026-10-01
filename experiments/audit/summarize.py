"""Markdown summary of the model-free checks: the oracle audit, the click hazard audit, the handoff pixel
calibration and the stall audit. Reads the JSONL rows those scripts wrote; writes no number by hand.

usage: python summarize.py results/vivian-4090 > results/vivian-4090/checks_report.md
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

VERDICTS = ("intended", "now_correct", "other_item", "nothing")
THRESHOLDS = (0.005, 0.02, 0.05, 0.1)


def load(paths):
    return [json.loads(line) for p in paths for line in open(p) if line.strip()]


def pct(x):
    return f"{100 * x:.0f}%"


def main(root: str) -> None:
    root = Path(root)
    out = ["# Model-free checks", ""]

    oracle = load(sorted(root.glob("audit/oracle_*.jsonl")))
    if oracle:
        ok = Counter(r["domain"] for r in oracle if r["ok"])
        n = Counter(r["domain"] for r in oracle)
        out += ["## Oracle audit", "",
                "An oracle that reads item positions from the page performs each scenario's committing flow on the "
                "correct target and on the stale one, under the after_handoff timing. A scenario passes when the "
                "scorer calls the first a success and the second stale (or the target is gone when the data says it "
                "should be).", "", "| domain | scenarios | pass |", "|---|---|---|"]
        out += [f"| {d} | {n[d]} | {pct(ok[d] / n[d])} |" for d in sorted(n)]
        out += [f"| all | {len(oracle)} | {pct(sum(ok.values()) / len(oracle))} |", ""]

    toctou = load(sorted(root.glob("audit/toctou_*.jsonl")))
    if toctou:
        t = defaultdict(Counter)
        for r in toctou:
            t[(r["domain"], r["change_kind"])][r["verdict"]] += 1
        out += ["## Click hazard (mid-step change)", "",
                "A click aimed at the planner's target from the screenshot lands after the change. Columns say what "
                "the click opened: the intended item, the item that is now correct, another item, or nothing.", "",
                "| domain | change | n | " + " | ".join(VERDICTS) + " |", "|---|---|---|" + "---|" * len(VERDICTS)]
        for (d, k), c in sorted(t.items()):
            m = sum(c.values())
            out.append(f"| {d} | {k} | {m} | " + " | ".join(pct(c[v] / m) for v in VERDICTS) + " |")
        out.append("")

    pixel = [r for r in load(sorted(root.glob("calibration/pixel_*.jsonl"))) if r["landed"]]
    if pixel:
        out += ["## Pixel change at the handoff", "",
                "Share of landed changes on which a pixel guard with each threshold would fire. Harmless: no change "
                "to the target (cosmetic or irrelevant). Relevant: the target moved or went away.", "",
                "| domain | " + " | ".join(f"> {t:g} harmless / relevant" for t in THRESHOLDS) + " |",
                "|---|" + "---|" * len(THRESHOLDS)]
        for d in sorted({r["domain"] for r in pixel}) + ["all"]:
            rs = [r for r in pixel if d == "all" or r["domain"] == d]
            harm = [r for r in rs if r["change_kind"] in ("none", "irrelevant")]
            rel = [r for r in rs if r["change_kind"] in ("relevant", "target_removed")]
            cells = [f"{pct(sum(r['changed_fraction'] > t for r in harm) / len(harm))} / "
                     f"{pct(sum(r['changed_fraction'] > t for r in rel) / len(rel))}" for t in THRESHOLDS]
            out.append(f"| {d} | " + " | ".join(cells) + " |")
        out.append("")
    stall = [r for r in load(sorted(root.glob("audit/stall_*.jsonl"))) if r["unchanged"] is not None]
    if stall:
        out += ["## Stall return on correct runs", "",
                "The oracle performs each scenario's correct flow; the stall return (`hierarchical_stall`) would "
                "interrupt it wherever two actions in a row leave the screenshot unchanged.", "",
                "| domain | scenarios | any unchanged action | two in a row (would be interrupted) |", "|---|---|---|---|"]
        for d in sorted({r["domain"] for r in stall}) + ["all"]:
            rs = [r for r in stall if d == "all" or r["domain"] == d]
            out.append(f"| {d} | {len(rs)} | {pct(sum(any(r['unchanged']) for r in rs) / len(rs))} | "
                       f"{pct(sum(r['longest_unchanged_run'] >= 2 for r in rs) / len(rs))} |")
        out.append("")
    print("\n".join(out))


if __name__ == "__main__":
    main(sys.argv[1])
