"""Local transformers backend (greedy decoding, batched). Needs the `models` extra and a GPU."""
import io
import os
from pathlib import Path
from typing import List, Sequence

from .base import Request


def conversation(r: Request) -> list:
    """Chat message in the layout the pilot used: text first, then the screenshot."""
    content = [{"type": "text", "text": r.prompt}]
    if r.image_png is not None:
        from PIL import Image
        content.append({"type": "image", "image": Image.open(io.BytesIO(r.image_png)).convert("RGB")})
    return [{"role": "user", "content": content}]


def snapshot_revision(path: str):
    """Commit hash of a Hugging Face cache snapshot directory, or None for any other directory."""
    p = Path(path)
    return p.name if p.parent.name == "snapshots" else None


class HFVLM:
    def __init__(self, model_id: str, batch: int = 8, dtype: str = os.environ.get("DTYPE", "bfloat16")):
        import torch
        from huggingface_hub import snapshot_download
        from transformers import AutoModelForImageTextToText, AutoProcessor
        local = model_id if os.path.isdir(model_id) else snapshot_download(model_id)
        self.name, self.batch, self._torch = model_id, batch, torch
        self.revision = snapshot_revision(local)
        self.proc = AutoProcessor.from_pretrained(local)
        self.proc.tokenizer.padding_side = "left"
        self.model = AutoModelForImageTextToText.from_pretrained(
            local, dtype=getattr(torch, dtype), device_map="cuda").eval()
        self.image_grid = None  # logged by runs: shows whether screenshots were resized

    def generate(self, requests: Sequence[Request]) -> List[str]:
        out = []
        for s in range(0, len(requests), self.batch):
            chunk = requests[s:s + self.batch]
            enc = self.proc.apply_chat_template([conversation(r) for r in chunk], tokenize=True,
                                                add_generation_prompt=True, return_dict=True,
                                                return_tensors="pt", padding=True).to("cuda")
            if self.image_grid is None and "image_grid_thw" in enc:
                self.image_grid = enc["image_grid_thw"][0].tolist()
            with self._torch.no_grad():
                g = self.model.generate(**enc, max_new_tokens=max(r.max_new_tokens for r in chunk), do_sample=False)
            out += self.proc.batch_decode(g[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        return out
