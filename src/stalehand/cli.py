"""Command line entry point: `stalehand <command> ...`."""
import argparse
import sys
from typing import List, Optional

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
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
