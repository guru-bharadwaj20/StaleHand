"""Command line entry point: `stalehand <command> ...`."""
import argparse
import os
import sys
from typing import List, Optional

from .models.registry import MODELS
from .scenarios import registry
from .scenarios.export import write_jsonl


def _csv(text: Optional[str]):
    return [t.strip() for t in text.split(",") if t.strip()] if text else None


def _scenarios(args) -> int:
    scen = registry.generate(args.domain, seed=args.seed, n=args.n, kinds=_csv(args.kinds),
                             variants=_csv(args.variants), change_step=args.change_step)
    n = write_jsonl(scen, args.out)
    print(f"wrote {n} scenarios to {args.out}")
    return 0


def _run_job(args) -> int:
    from .run import execute as ex
    from .run.job import decode
    from .run.loader import backend_of, model_loader
    try:
        job = decode(args.job)
    except ValueError as e:  # includes malformed base64 and JSON
        print(f"bad job: {e}", file=sys.stderr)
        return 2

    def make_env(timing):
        from .env.browser import BrowserEnv
        return BrowserEnv(change_timing=timing)
    ex.execute(job, args.out, root=args.root, load_model=model_loader(os.environ), make_env=make_env,
               backend=backend_of(os.environ))
    return 0


def _serve(args) -> int:
    from .models import hf, serve
    model = hf.HFVLM(MODELS[args.model].hf_id, batch=args.max_batch)
    httpd = serve.make_server(model, args.host, args.port, max_batch=args.max_batch)
    print(f"serving {MODELS[args.model].hf_id} on {args.host}:{args.port}", flush=True)
    httpd.serve_forever()
    return 0


def _report(args) -> int:
    from .report.build import markdown
    from .report.tables import load_rows
    rows = load_rows(args.runs)
    if not rows:
        print(f"no results.jsonl under {args.runs}", file=sys.stderr)
        return 1
    text = markdown(rows, baseline=args.baseline, n_boot=args.n_boot, seed=args.seed)
    if args.charts:
        from pathlib import Path

        from .report.charts import relevant_outcomes, tradeoff
        out = Path(args.out)
        links = []
        for arch in dict.fromkeys(r["architecture"] for r in rows):
            for kind, draw, title in (("tradeoff", tradeoff, "Success against false alarms"),
                                      ("outcomes", relevant_outcomes, "Episodes with a relevant change")):
                name = f"{out.stem}_{arch}_{kind}.svg"
                (out.parent / name).write_text(draw(rows, arch, f"{title} ({arch})"))
                links.append(f"![{title} ({arch})]({name})")
        head, _, tail = text.partition("## Summary by guard")
        text = head + "\n\n".join(links) + "\n\n## Summary by guard" + tail
    with open(args.out, "w") as f:
        f.write(text)
    print(f"wrote {args.out} from {len(rows)} episodes")
    return 0


def _readme(args) -> int:
    from .report.readme import section, splice
    with open(args.readme, encoding="utf-8") as f:
        doc = f.read()
    new = splice(doc, section(args.results))
    if args.check:
        if new != doc:
            print(f"{args.readme} results section is out of date; run `stalehand readme`", file=sys.stderr)
            return 1
        return 0
    with open(args.readme, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print(f"updated the results section of {args.readme}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="stalehand")
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("scenarios", help="generate scenarios as JSONL")
    s.add_argument("--domain", required=True, choices=sorted(registry.DOMAINS))
    s.add_argument("--n", type=int, default=40, help="first screens per task kind")
    s.add_argument("--seed", type=int, default=0)
    s.add_argument("--kinds", help="comma-separated task kinds (default: all)")
    s.add_argument("--variants", help="comma-separated change variants (default: all)")
    s.add_argument("--change-step", type=int, default=1)
    s.add_argument("--out", required=True)
    s.set_defaults(func=_scenarios)
    r = sub.add_parser("run-job", help="run one job from the Go runner (see stalehand.run)")
    r.add_argument("--job", required=True, help="base64 JSON job spec, as runner/launch writes it")
    r.add_argument("--out", required=True, help="run directory; a rerun resumes it")
    r.add_argument("--root", default=".", help="directory that scenario paths are relative to")
    r.set_defaults(func=_run_job)
    v = sub.add_parser("serve", help="serve one model over an OpenAI-compatible HTTP API (transformers, no vLLM)")
    v.add_argument("--model", required=True, choices=sorted(MODELS), help="short name from the model registry")
    v.add_argument("--host", default="127.0.0.1", help="interface to listen on; reachable from other boxes only if set")
    v.add_argument("--port", type=int, default=8000)
    v.add_argument("--max-batch", type=int, default=8, help="requests run together on the GPU")
    v.set_defaults(func=_serve)
    rp = sub.add_parser("report", help="markdown report from the results.jsonl files under a directory")
    rp.add_argument("--runs", required=True)
    rp.add_argument("--out", required=True)
    rp.add_argument("--baseline", default="none", help="guard the others are paired against")
    rp.add_argument("--n-boot", type=int, default=10000)
    rp.add_argument("--seed", type=int, default=0)
    rp.add_argument("--charts", action="store_true", help="also write SVG charts next to the report")
    rp.set_defaults(func=_report)
    rd = sub.add_parser("readme", help="rebuild the results section of README.md from result files")
    rd.add_argument("--results", default="results")
    rd.add_argument("--readme", default="README.md")
    rd.add_argument("--check", action="store_true", help="exit 1 if the section is out of date, change nothing")
    rd.set_defaults(func=_readme)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
