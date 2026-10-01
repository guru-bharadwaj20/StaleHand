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
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
