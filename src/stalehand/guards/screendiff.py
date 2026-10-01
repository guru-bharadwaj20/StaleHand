"""Python side of the Rust `screendiff` tool (crates/screendiff): compare two PNG screenshots."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Sequence

_BUILT = Path(__file__).resolve().parents[3] / "crates" / "screendiff" / "target" / "release" / "screendiff"


def binary() -> Optional[str]:
    for candidate in (os.environ.get("STALEHAND_SCREENDIFF"), str(_BUILT), shutil.which("screendiff")):
        if candidate and Path(candidate).is_file():
            return candidate
    return None


def compare(before_png: bytes, after_png: bytes, region: Optional[Sequence[int]] = None, threshold: float = 8.0) -> dict:
    exe = binary()
    if exe is None:
        raise FileNotFoundError("screendiff not found; run `cargo build --release` in crates/screendiff")
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d) / "a.png", Path(d) / "b.png"
        a.write_bytes(before_png)
        b.write_bytes(after_png)
        cmd = [exe, str(a), str(b), "--threshold", str(threshold)]
        if region is not None:
            cmd += ["--region", ",".join(str(int(v)) for v in region)]
        out = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
    return json.loads(out.stdout)
