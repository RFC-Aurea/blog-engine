#!/usr/bin/env python3
"""Download a finished Gamma image into the run folder so it can be looked at before upload, and write its report.

  python3 scripts/fetch_image.py --check
  python3 scripts/fetch_image.py <gamma image url> RUN/img/imageN.jpg [--prompt RUN/img/imageN.prompt.txt] [--credits N]

--check: exit 0 when cdn.gamma.app answers, 4 when the environment blocks it (then draw the images instead, and do
not spend Gamma credits). Run it before mcp__Gamma__generate_image.
The image is resized to 1800 px wide and saved as JPEG; RUN/img/imageN.report.json records generator, URL, md5,
size, the prompt's md5 and the credits left. The image still has to be looked at (Read tool) before it is pushed
and uploaded (rules/images.md).
"""
import hashlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

WIDTH = 1800
HOST = "https://cdn.gamma.app/"


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def reachable():
    r = subprocess.run(["curl", "-sS", "-o", "/dev/null", "-m", "15", "-w", "%{http_code}", HOST], capture_output=True, text=True)
    return r.returncode == 0 and r.stdout not in ("", "000")


def fit(raw):
    """Resize to 1800 px wide and save as JPEG (keeps Gamma's aspect ratio)."""
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    out = io.BytesIO()
    im.save(out, "JPEG", quality=90, optimize=True, progressive=True)
    return out.getvalue(), im.width, im.height


def main():
    if "--check" in sys.argv:
        ok = reachable()
        print("cdn.gamma.app reachable" if ok else "cdn.gamma.app is blocked in this environment: draw the images instead")
        sys.exit(0 if ok else 4)
    pos = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in ("--prompt", "--credits")]
    if len(pos) != 2:
        sys.exit(print(__doc__) or 1)
    url, out = pos[0], Path(pos[1])
    if not re.fullmatch(r"https://cdn\.gamma\.app/[A-Za-z0-9._/-]+", url):
        sys.exit(print("only https://cdn.gamma.app/ image URLs are accepted") or 1)
    r = subprocess.run(["curl", "-fsSL", "--retry", "2", "-m", "120", url], capture_output=True)
    if r.returncode:
        sys.exit(print(f"cannot download {url} (is cdn.gamma.app allowed in the environment?)") or 4)
    data, w, h = fit(r.stdout)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    prompt = Path(arg("--prompt")).read_text(encoding="utf-8").strip() if arg("--prompt") else None
    rep = {"ok": True, "generator": "gamma", "source_url": url, "output": str(out), "width": w, "height": h,
           "bytes": len(data), "md5": hashlib.md5(data).hexdigest(),
           "prompt_md5": hashlib.md5(prompt.encode()).hexdigest() if prompt else None,
           "credits_remaining": int(arg("--credits")) if arg("--credits") else None}
    out.with_suffix(".report.json").write_text(json.dumps(rep, indent=1) + "\n")
    print(json.dumps(rep))


if __name__ == "__main__":
    main()
