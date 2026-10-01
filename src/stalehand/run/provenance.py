"""What a run directory's config.json records, so any result can be traced to code, weights and libraries."""
import os
import platform
import socket
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from importlib import metadata
from typing import Dict, Iterable, Optional

PACKAGES = ("stalehand", "playwright", "pillow", "torch", "transformers", "accelerate", "huggingface-hub")


def git_state(root) -> Optional[dict]:
    def git(*args):
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        return None
    return {"commit": head.stdout.strip(), "dirty": bool(git("status", "--porcelain").stdout.strip())}


def versions(packages: Iterable[str] = PACKAGES) -> Dict[str, Optional[str]]:
    out = {}
    for p in packages:
        try:
            out[p] = metadata.version(p)
        except metadata.PackageNotFoundError:
            out[p] = None
    return out


def model_info(short: str, model, backend: str) -> dict:
    return {"name": short, "id": model.name, "revision": getattr(model, "revision", None), "backend": backend}


def config(job, models: dict, root) -> dict:
    return {"job": asdict(job), "seed": job.seed, "models": models, "git": git_state(root),
            "versions": versions(), "python": sys.version.split()[0], "platform": platform.platform(),
            "host": socket.gethostname(), "started": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            # how the models were reached and served (backend, URLs, STALEHAND_PRECISION such as fp8 on the Ada)
            "serving": {k: v for k, v in sorted(os.environ.items()) if k.startswith("STALEHAND_")}}
