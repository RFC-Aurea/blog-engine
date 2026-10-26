#!/usr/bin/env python3
"""Make one painted illustration or natural photo with an image model, save it in the run folder, write its report.

  python3 scripts/gen_image.py RUN/img/image1.prompt.txt RUN/img/image1.jpg [--aspect 16:9] [--model <id>]
  python3 scripts/gen_image.py --url https://cdn.gamma.app/... RUN/img/image1.jpg

Gemini (default): needs GEMINI_API_KEY in the environment and generativelanguage.googleapis.com reachable
(rules/images.md). The model comes from config.json "images.model", falling back to "images.fallback_model".
--url downloads a finished Gamma image instead (only cdn.gamma.app, and only once that host is allowed).

The output is resized to 1800 px wide and saved as JPEG; RUN/img/imageN.report.json records generator, model,
md5, size and attempts. The image still has to be looked at (Read tool) before it is pushed and uploaded.
Exit code 4: no key / host not reachable (fall back to drawn images); 1: the model returned no image.
"""
import base64
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import config  # noqa: E402

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
WIDTH = 1800


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def gemini(prompt, model, aspect):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit(print("GEMINI_API_KEY is not set: draw the images instead (rules/images.md)") or 4)
    gen = {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": {"aspectRatio": aspect}}
    if "pro" in model:
        gen["imageConfig"]["imageSize"] = "2K"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": gen}).encode()
    req = urllib.request.Request(API.format(model=model), data=body, method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:600]
        raise RuntimeError(f"{model}: HTTP {e.code} {detail}")
    except urllib.error.URLError as e:
        sys.exit(print(f"cannot reach the Gemini API ({e.reason}): draw the images instead") or 4)
    parts = [p for c in res.get("candidates", []) for p in (c.get("content") or {}).get("parts", [])]
    images = [p["inlineData"]["data"] for p in parts if p.get("inlineData") and not p.get("thought")]
    if not images:
        why = res.get("promptFeedback") or [c.get("finishReason") for c in res.get("candidates", [])]
        raise RuntimeError(f"{model}: no image returned ({why})")
    return base64.b64decode(images[-1])


def download(url):
    if not re.fullmatch(r"https://cdn\.gamma\.app/[A-Za-z0-9._/-]+", url):
        sys.exit(print("only https://cdn.gamma.app/ image URLs are accepted") or 1)
    r = subprocess.run(["curl", "-fsSL", "--retry", "2", "-m", "120", url], capture_output=True)
    if r.returncode:
        sys.exit(print(f"cannot download {url} (is cdn.gamma.app allowed in the environment?)") or 4)
    return r.stdout


def fit(raw):
    """Resize to 1800 px wide and save as JPEG (keeps the model's aspect ratio)."""
    try:
        from PIL import Image
    except ImportError:
        return raw, None, None
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    return out.getvalue(), im.width, im.height


def main():
    pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in ("--url", "--aspect", "--model")]
    if len(pos) != (1 if "--url" in sys.argv else 2):
        sys.exit(print(__doc__) or 1)
    out = Path(pos[-1])
    cfg = config().get("images", {})
    attempts, model = [], None
    if "--url" in sys.argv:
        raw, generator, prompt_md5 = download(arg("--url")), "gamma", None
    else:
        if not os.environ.get("GEMINI_API_KEY"):
            sys.exit(print("GEMINI_API_KEY is not set: draw the images instead (rules/images.md)") or 4)
        prompt = Path(pos[0]).read_text(encoding="utf-8").strip()
        prompt_md5, generator, raw = hashlib.md5(prompt.encode()).hexdigest(), "gemini", None
        for model in [m for m in (arg("--model"), cfg.get("model"), cfg.get("fallback_model")) if m]:
            try:
                raw = gemini(prompt, model, arg("--aspect", cfg.get("aspect", "16:9")))
                attempts.append({"model": model, "ok": True})
                break
            except RuntimeError as e:
                attempts.append({"model": model, "ok": False, "error": str(e)[:300]})
                print(e, file=sys.stderr)
        if raw is None:
            sys.exit(print("no image from any model") or 1)
    data, w, h = fit(raw)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    rep = {"ok": True, "generator": generator, "model": model if generator == "gemini" else None,
           "output": str(out), "width": w, "height": h, "bytes": len(data),
           "md5": hashlib.md5(data).hexdigest(), "prompt_md5": prompt_md5, "attempts": attempts,
           "source_url": arg("--url")}
    out.with_suffix(".report.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
