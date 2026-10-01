"""Static SVG charts for reports, written without a plotting library so they render anywhere the report does.

Colours are the dataviz reference palette's first four categorical slots on its light surface, checked with its
validator (all hard gates pass; aqua and yellow sit below 3:1 contrast, so every chart ships next to the report's
tables, which carry the same numbers).
"""
from html import escape
from typing import Dict, List

from .tables import guard_summary

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
FONT = "font-family=\"Noto Sans, Helvetica, Arial, sans-serif\""


def _text(x, y, s, size=12, color=INK, anchor="start", weight="normal") -> str:
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {FONT}>{escape(s)}</text>')


def _svg(w, h, body: List[str], label: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{escape(label)}"><rect width="{w}" height="{h}" fill="{SURFACE}"/>'
            + "".join(body) + "</svg>\n")


def tradeoff(rows: List[dict], architecture: str, title: str) -> str:
    """One dot per guard: false alarms on harmless changes (x) against success when the change matters (y)."""
    pts = [g for g in guard_summary(rows) if g["architecture"] == architecture
           and g["relevant_success"] is not None and g["false_alarm"] is not None]
    w, h, left, right, top, bottom = 680, 440, 70, 190, 50, 60
    pw, ph = w - left - right, h - top - bottom
    X = lambda v: left + v * pw
    Y = lambda v: top + (1 - v) * ph
    body = [_text(left, 28, title, 15, weight="600")]
    for t in (0, 0.25, 0.5, 0.75, 1):
        body.append(f'<line x1="{X(0)}" x2="{X(1)}" y1="{Y(t)}" y2="{Y(t)}" stroke="{GRID}" stroke-width="1"/>')
        body.append(f'<line x1="{X(t)}" x2="{X(t)}" y1="{Y(0)}" y2="{Y(1)}" stroke="{GRID}" stroke-width="1"/>')
        body.append(_text(left - 8, Y(t) + 4, f"{t:.0%}", 11, MUTED, "end"))
        body.append(_text(X(t), Y(0) + 18, f"{t:.0%}", 11, MUTED, "middle"))
    body.append(_text(left + pw / 2, h - 14, "False alarms on harmless changes", 12, MUTED, "middle"))
    body.append(f'<g transform="translate(18 {top + ph / 2}) rotate(-90)">'
                + _text(0, 0, "Success when the change matters", 12, MUTED, "middle") + "</g>")
    placed: List[float] = []
    for g in sorted(pts, key=lambda g: -g["relevant_success"]):
        x, y = X(g["false_alarm"]), Y(g["relevant_success"])
        body.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{SERIES[0]}" stroke="{SURFACE}" stroke-width="2"/>')
        ly = y + 4
        while any(abs(ly - p) < 14 for p in placed):  # keep labels of nearby dots from overlapping
            ly += 14
        placed.append(ly)
        body.append(_text(x + 10, ly, f'{g["guard"]} ({g["calls"]:.1f} calls)', 11))
    return _svg(w, h, body, f"{title}: success when the change matters against false alarms, one dot per guard")


OUTCOME_GROUPS = (("success", ("success",)), ("stale target", ("stale",)),
                  ("wrong item or detail", ("wrong_item", "wrong_detail")), ("no commit", ("no_commit", "aborted")))


def relevant_outcomes(rows: List[dict], architecture: str, title: str) -> str:
    """Per guard, how episodes with a relevant change ended, as 100% stacked bars."""
    rel = [r for r in rows if r["architecture"] == architecture and r["change_kind"] == "relevant"]
    guards: Dict[str, List[dict]] = {}
    for r in rel:
        guards.setdefault(r["guard"], []).append(r)
    order = sorted(guards, key=lambda g: -sum(r["outcome"] == "success" for r in guards[g]) / len(guards[g]))
    w, left, right, top, bar, gap = 700, 210, 30, 76, 22, 12
    h = top + len(order) * (bar + gap) + 20
    pw = w - left - right
    body = [_text(left, 28, title, 15, weight="600")]
    lx = left
    for i, (name, _) in enumerate(OUTCOME_GROUPS):
        body.append(f'<rect x="{lx}" y="44" width="12" height="12" rx="2" fill="{SERIES[i]}"/>')
        body.append(_text(lx + 18, 54, name, 12))
        lx += 18 + 7 * len(name) + 22
    for row_i, g in enumerate(order):
        y = top + row_i * (bar + gap)
        n = len(guards[g])
        body.append(_text(left - 10, y + bar / 2 + 4, f"{g} (n={n})", 12, INK, "end"))
        x = float(left)
        for i, (_, kinds) in enumerate(OUTCOME_GROUPS):
            share = sum(r["outcome"] in kinds for r in guards[g]) / n
            if share <= 0:
                continue
            seg = share * pw
            body.append(f'<rect x="{x:.1f}" y="{y}" width="{max(seg - 2, 0.5):.1f}" height="{bar}" rx="2" '
                        f'fill="{SERIES[i]}"><title>{escape(g)}: {OUTCOME_GROUPS[i][0]} {share:.0%}</title></rect>')
            x += seg
    return _svg(w, h, body, f"{title}: outcomes of episodes with a relevant change, per guard")
