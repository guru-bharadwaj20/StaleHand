"""Find the built web app for a domain (apps/dist/<domain>.html, or $STALEHAND_APPS/<domain>.html)."""
import os
from pathlib import Path

DEFAULT_DIR = Path(__file__).resolve().parents[3] / "apps" / "dist"


def app_url(domain: str) -> str:
    base = Path(os.environ.get("STALEHAND_APPS", DEFAULT_DIR))
    path = base / f"{domain}.html"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found; run `npm run build` in apps/ first")
    return path.as_uri()
