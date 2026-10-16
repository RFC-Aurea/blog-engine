"""Shared helpers for the blog engine scripts (standard library only)."""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent

STOPWORDS = set("""a an and are as at be but by can do does for from how i if in is it its me my no not
of on or our s so than that the their them then there these they this to up vs was what when where which
who why will with you your yours about after before during into over under can't don't much""".split())

# Words that mean the same thing for matching and duplicate detection.
SYN = {"sign": "symptom", "symptoms": "symptom", "cost": "price", "prices": "price", "pricing": "price",
       "costs": "price", "chance": "rate", "odds": "rate", "rates": "rate", "meaning": "mean", "means": "mean",
       "pregnant": "pregnancy", "pregnancies": "pregnancy", "conceive": "pregnancy", "conceiving": "pregnancy",
       "getting": "get", "treatments": "treatment", "eggs": "egg", "embryos": "embryo", "test": "testing",
       "tests": "testing", "levels": "level", "naturally": "natural", "women": "woman", "doctors": "doctor",
       "freezing": "freeze", "frozen": "freeze"}


def load_json(path, default=None):
    p = ROOT / path if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))


def save_json(path, data):
    p = ROOT / path if not pathlib.Path(path).is_absolute() else pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def config():
    return load_json("config.json")


def split_source(text):
    """Split post.md into (front_matter_dict, body_markdown)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise SystemExit("post.md must start with a --- JSON front matter --- block")
    try:
        fm = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"front matter is not valid JSON: {e}")
    return fm, m.group(2)


def words(text):
    return re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text.lower())


def core_words(text):
    """Content words used for keyword matching and similarity (light stemming)."""
    out = []
    for w in words(text):
        if w in STOPWORDS or len(w) < 2:
            continue
        if w in SYN:
            out.append(SYN[w])
            continue
        for suf in ("ing", "ies", "es", "s"):
            if len(w) > 4 and w.endswith(suf):
                w = w[: -len(suf)] + ("y" if suf == "ies" else "")
                break
        out.append(SYN.get(w, w))
    return out


def similarity(a, b):
    """Word-overlap similarity (Jaccard on content words)."""
    sa, sb = set(core_words(a)), set(core_words(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def contains_keyword(text, keyword):
    """True when every content word of the keyword appears in the text."""
    kw = set(core_words(keyword))
    return bool(kw) and kw <= set(core_words(text))


def strip_md(text):
    """Markdown inline -> plain text."""
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1", text)
    text = text.replace("**", "").replace("*", "")
    return text


def brand_allowed_urls(brand):
    """Verified internal pages from the brand file plus live post URLs."""
    cfg = config()["brands"][brand]
    md = (ROOT / cfg["brand_file"]).read_text(encoding="utf-8")
    section = md.split("Unverified paths")[0]
    urls = set(re.findall(r"https://[^\s|)]+", section))
    for p in load_json("data/published.json", {"posts": []})["posts"]:
        if p["brand"] == brand:
            urls.add(cfg["post_base"] + p["slug"])
    return {u.rstrip("/") for u in urls}
