"""Set IMAGE1 to drawn figure1.png and IMAGE2 to Gamma photo.jpg. usage: set_fig2.py RUN FIG_ID FIG_HASH PHOTO_ID PHOTO_HASH FIG_ALT [PHOTO_ALT]"""
import json, sys, hashlib
from pathlib import Path
run = Path(sys.argv[1]); fid, fh, pid, ph, falt = sys.argv[2:7]
plan = {p["run"]: p for p in json.load(open("runs/backfill-2026-10-26/plan.json"))["posts"]}
palt = sys.argv[7] if len(sys.argv) > 7 else plan[run.name]["photo"]["alt"]
p = run / "post.md"; s = p.read_text(); end = s.index("\n---\n", 4); fm = json.loads(s[4:end])
spec = json.loads((run / "img/figure1.json").read_text())
old = fm["images"]
md5 = lambda f: hashlib.md5((run / f).read_bytes()).hexdigest()
assert md5("img/figure1.png") == fh and md5("img/photo.jpg") == ph, "hash mismatch"
why = "Alifiya asked for research-grade medical illustrations drawn by Claude plus a Gamma photo cover (2026-10-26)"
fm.setdefault("replaced_images", {})["2026-10-26 illustration"] = {
    k: {kk: old[k].get(kk) for kk in ("generator", "wix_id", "alt", "file")} | {"why": why} for k in ("IMAGE1", "IMAGE2")}
rep = json.loads((run / "img/photo.report.json").read_text())
fm["images"]["IMAGE1"] = {
    "generator": "drawn", "kind": "medical illustration", "source": "img/figure1.html", "file": "img/figure1.png",
    "width": 1800, "height": 945, "md5": fh, "wix_id": fid, "wix_hash": fh, "alt": falt,
    "labels": [l["text"] for l in spec["labels"]] + [l["sub"] for l in spec["labels"] if l.get("sub")],
    "reviewed": True, "preview_src": "img/figure1.png"}
fm["images"]["IMAGE2"] = {
    "generator": "gamma", "gamma_url": rep["source_url"], "kind": "photo", "source": "img/photo.prompt.txt",
    "file": "img/photo.jpg", "width": rep["width"], "height": rep["height"], "md5": ph, "wix_id": pid, "wix_hash": ph,
    "alt": palt, "labels": [], "reviewed": True, "preview_src": "img/photo.jpg"}
fm["hero"] = "IMAGE2"
assert len(falt) < 125 and len(palt) < 125, (len(falt), len(palt))
p.write_text("---\n" + json.dumps(fm, indent=1, ensure_ascii=False) + s[end:])
print(run.name, "ok |", palt)
