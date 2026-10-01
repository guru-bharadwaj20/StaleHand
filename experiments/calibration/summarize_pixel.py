"""Fire rates of the pixel guard at the handoff, per threshold: on harmless changes (false alarms) and on relevant
ones (catches), from the rows pixel_handoff.py writes. Only scenarios whose change actually landed are counted.

usage: python summarize_pixel.py pixel_*.jsonl
"""
import json
import sys

THRESHOLDS = (0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2)


def main(paths) -> None:
    rows = [json.loads(line) for p in paths for line in open(p) if line.strip()]
    rows = [r for r in rows if r["landed"]]
    domains = sorted({r["domain"] for r in rows})
    print(f"{len(rows)} landed changes")
    print("domain   " + " ".join(f"{t:>14}" for t in THRESHOLDS))
    for dom in domains + ["all"]:
        rs = [r for r in rows if dom == "all" or r["domain"] == dom]
        harmless = [r for r in rs if r["change_kind"] in ("none", "irrelevant")]
        relevant = [r for r in rs if r["change_kind"] in ("relevant", "target_removed")]
        cells = []
        for t in THRESHOLDS:
            fa = sum(r["changed_fraction"] > t for r in harmless) / len(harmless) if harmless else float("nan")
            hit = sum(r["changed_fraction"] > t for r in relevant) / len(relevant) if relevant else float("nan")
            cells.append(f"{100 * fa:4.0f}% / {100 * hit:4.0f}%")
        print(f"{dom:8} " + " ".join(f"{c:>14}" for c in cells))
    print("cells: fires on harmless / fires on relevant")


if __name__ == "__main__":
    main(sys.argv[1:])
