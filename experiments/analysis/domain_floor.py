"""Why the new domains sit at the floor, read from the result files.

The eight-guard domain run (`results/vivian-4090/domains/`) leaves files and tickets at 0% under every guard. This
reads the result rows and the trajectories to show where each domain stalls: the success rate per guard, the mix of
executor actions, and the furthest point each episode reaches in the app's own event log. A domain whose task needs a
typed value (a share recipient, a ticket assignee) can only commit after a `type` action; a domain reached by clicks
alone (join a meeting, send a pre-filled reply) does not.

usage: python domain_floor.py report results/vivian-4090/domains > floor_report.md
"""
import argparse
import collections
import json
from pathlib import Path

# The committing event for each domain, and whether reaching it needs a typed value in the form before the commit.
COMMIT = {
    "files": ("share", True),
    "tickets": ("assign", True),
    "calendar": ("join", False),
    "chat": ("send", True),
    "inbox": ("send", False),  # the reply body is pre-filled; only forward needs a typed recipient
    "shop": ("add_to_cart", False),
}


def domain_of(scenario_id):
    return scenario_id.split("-")[0]


def results_rows(roots):
    for root in roots:
        for path in Path(root).rglob("results.jsonl"):
            for line in path.open():
                yield json.loads(line)


def trajectories(roots):
    for root in roots:
        for path in Path(root).rglob("trajectories/*.json"):
            yield json.loads(path.read_text())


def report(roots):
    rows = list(results_rows(roots))
    guards = sorted({r["guard"] for r in rows})
    domains = sorted({domain_of(r["scenario_id"]) for r in rows})

    cell = collections.defaultdict(collections.Counter)
    for r in rows:
        c = cell[(domain_of(r["scenario_id"]), r["guard"])]
        c["n"] += 1
        c[r["outcome"]] += 1
        if r["end_reason"] == "max_steps":
            c["max_steps"] += 1

    actions = collections.defaultdict(collections.Counter)
    stage = collections.defaultdict(collections.Counter)
    typed_eps = collections.Counter()
    eps = collections.Counter()
    for t in trajectories(roots):
        d = domain_of(t["scenario_id"])
        eps[d] += 1
        saw_type = False
        for e in t["entries"]:
            act = e.get("action")
            if e.get("kind") == "action" and isinstance(act, dict):
                actions[d][act["type"]] += 1
                saw_type = saw_type or act["type"] == "type"
        if saw_type:
            typed_eps[d] += 1
        evs = t.get("app_events", [])
        stage[d][evs[-1]["kind"] if evs else "(none)"] += 1

    out = [
        "Where each new domain stalls, from the result rows and trajectories. `success` is a committed, correct "
        "target; `ran out` is the share of episodes that hit the step limit.",
        "",
        "## Success per guard",
        "",
        "| domain | " + " | ".join(guards) + " |",
        "|---" * (len(guards) + 1) + "|",
    ]
    for d in domains:
        pct = []
        for g in guards:
            c = cell[(d, g)]
            pct.append(f"{100 * c['success'] / c['n']:.0f}%" if c["n"] else "-")
        out.append(f"| {d} | " + " | ".join(pct) + " |")

    out += ["", "## Executor actions and how far each episode gets", "",
            "| domain | episodes | needs typed value | episodes that typed | click | type | scroll | done | "
            "most common furthest event |", "|---|---|---|---|---|---|---|---|---|"]
    for d in domains:
        a = actions[d]
        needs = "yes" if COMMIT.get(d, ("", False))[1] else "no"
        top = ", ".join(f"{k} {v}" for k, v in stage[d].most_common(3))
        out.append(f"| {d} | {eps[d]} | {needs} | {typed_eps[d]} | {a['click']} | {a['type']} | {a['scroll']} | "
                   f"{a['done']} | {top} |")

    out += ["", "## Reading", "",
            "Files and tickets commit only through a typed value (a share recipient, a ticket assignee), and the "
            "executor almost never types: it reaches the form, then clicks the empty field until the step budget "
            "runs out. Calendar commits by clicking Join and is the one domain that separates the guards. Because "
            "every files and tickets episode fails at the same step, before any guard's decision changes the "
            "outcome, all guards tie at the floor and the run measures the executor, not the guards."]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    rep = sub.add_parser("report", help="markdown report to stdout")
    rep.add_argument("roots", nargs="+", help="run-set directories (each holds results.jsonl and trajectories/)")
    args = ap.parse_args()
    if args.cmd == "report":
        print(report(args.roots), end="")


if __name__ == "__main__":
    main()
