// Local check that templates/publish.js rebuilds exactly the rich content build_post.py produced.
// Usage: node scripts/test_publish_js.js runs/<run>
const fs = require("fs");
const path = require("path");
const run = process.argv[2];
const src = fs.readFileSync(path.join(__dirname, "..", "templates", "publish.js"), "utf8");
const compact = JSON.parse(fs.readFileSync(path.join(run, "compact.json"), "utf8"));
const full = JSON.parse(fs.readFileSync(path.join(run, "payload.json"), "utf8"));
compact.dryRun = true;
const files = [{ path: "compact.json", content: JSON.stringify(compact) }];
const fn = new Function("files", "wix", "return (" + src + ")")(files, {});
const strip = (o) => {
  if (Array.isArray(o)) return o.map(strip);
  if (o && typeof o === "object") {
    const out = {};
    for (const k of Object.keys(o).sort()) {
      if (k === "id" && o.type && o.type !== "HEADING") continue;
      if (k === "id" && o.type === "HEADING" && !(o.headingData && o.headingData.level === 2)) continue;
      out[k] = strip(o[k]);
    }
    return out;
  }
  return o;
};
fn().then((res) => {
  const a = JSON.stringify(strip(res.body));
  const b = JSON.stringify(strip(full));
  const want = require("child_process").execFileSync("python3", ["-c",
    "import json,sys; sys.path.insert(0, 'scripts'); from common import content_hash; " +
    "print(content_hash(json.load(open(sys.argv[1], encoding='utf-8'))))", path.join(run, "compact.json")],
    { cwd: path.join(__dirname, "..") }).toString().trim();
  if (res.inputHash !== want) {
    console.log("HASH MISMATCH: js " + res.inputHash + " vs python " + want);
    process.exit(1);
  }
  if (a === b) {
    console.log("MATCH: publish.js rebuilds the same payload (" + b.length + " chars, hash " + want + ")");
  } else {
    let i = 0;
    while (i < a.length && a[i] === b[i]) i++;
    console.log("MISMATCH at char " + i);
    console.log("js  : " + a.slice(Math.max(0, i - 200), i + 200));
    console.log("py  : " + b.slice(Math.max(0, i - 200), i + 200));
    process.exit(1);
  }
});
