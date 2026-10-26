#!/usr/bin/env node
// Render a labelled illustration (HTML/SVG, 1200x630 design canvas) to PNG with the sandbox's Chromium,
// then check the labels: every <text> must sit inside the canvas and no two labels may overlap.
//
//   node scripts/render_image.js RUN/image1.html RUN/image1.png [--scale 1.5]
//
// {{BASE_CSS}}, {{COMPONENTS}} and {{MEDICAL}} in the HTML are replaced with illustrations/base.css,
// illustrations/components.svg and illustrations/medical.svg (the research-grade anatomy library), so every image
// shares one palette, one typeface and one part library.
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [input, output] = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const scaleArg = process.argv.indexOf("--scale");
const scale = scaleArg > 0 ? Number(process.argv[scaleArg + 1]) : 1.5;
if (!input || !output) {
  console.error("usage: node scripts/render_image.js <in.html> <out.png> [--scale 1.5]");
  process.exit(1);
}
const W = 1200, H = 630, MARGIN = 12;
const lib = path.join(__dirname, "..", "illustrations");
let html = fs.readFileSync(input, "utf8")
  .replace("{{BASE_CSS}}", fs.readFileSync(path.join(lib, "base.css"), "utf8"))
  .replace("{{COMPONENTS}}", fs.readFileSync(path.join(lib, "components.svg"), "utf8"))
  .replace("{{MEDICAL}}", () => fs.readFileSync(path.join(lib, "medical.svg"), "utf8"));

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: scale });
  await page.setContent(html, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  const report = await page.evaluate(({ W, H, MARGIN }) => {
    const boxes = [...document.querySelectorAll("svg text")]
      .filter((t) => t.textContent.trim() && !t.closest("symbol, defs"))
      .map((t) => {
        const r = t.getBoundingClientRect();
        return { text: t.textContent.trim().slice(0, 40), x: r.x, y: r.y, w: r.width, h: r.height };
      });
    const problems = [];
    for (const b of boxes) {
      if (b.x < MARGIN || b.y < MARGIN || b.x + b.w > W - MARGIN || b.y + b.h > H - MARGIN)
        problems.push(`outside canvas: "${b.text}"`);
    }
    for (let i = 0; i < boxes.length; i++)
      for (let j = i + 1; j < boxes.length; j++) {
        const a = boxes[i], b = boxes[j];
        const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
        const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
        if (ox > 2 && oy > 2) problems.push(`labels overlap: "${a.text}" / "${b.text}"`);
      }
    // labels must not run out of the card they start in
    const cards = [...document.querySelectorAll("svg.canvas rect.card")].map((c) => c.getBoundingClientRect());
    for (const b of boxes) {
      const home = cards.find((c) => b.x >= c.x && b.x <= c.x + c.width && b.y + b.h / 2 >= c.y && b.y + b.h / 2 <= c.y + c.height);
      if (home && (b.x + b.w > home.x + home.width - 8 || b.y + b.h > home.y + home.height - 4))
        problems.push(`label runs out of its card: "${b.text}"`);
    }
    const fonts = [...new Set([...document.querySelectorAll("svg text")].map((t) => getComputedStyle(t).fontFamily))];
    const minSize = Math.min(...[...document.querySelectorAll("svg text")].map((t) => parseFloat(getComputedStyle(t).fontSize)));
    return { labels: boxes.length, problems, fonts, minSize };
  }, { W, H, MARGIN });
  await page.screenshot({ path: output, clip: { x: 0, y: 0, width: W, height: H } });
  // labels must not sit on a drawing: render again without labels and leader lines, and every label box must be
  // (almost) one flat colour underneath
  await page.addStyleTag({ content: "svg text, .leader, .leader-dot { visibility: hidden !important; }" });
  const bare = (await page.screenshot({ clip: { x: 0, y: 0, width: W, height: H } })).toString("base64");
  const onDrawing = await page.evaluate(async ({ bare, scale }) => {
    const img = new Image();
    img.src = "data:image/png;base64," + bare;
    await img.decode();
    const c = document.createElement("canvas");
    c.width = img.width; c.height = img.height;
    const ctx = c.getContext("2d");
    ctx.drawImage(img, 0, 0);
    const out = [];
    for (const t of document.querySelectorAll("svg.canvas text")) {
      if (!t.textContent.trim() || t.closest("symbol, defs")) continue;
      const r = t.getBoundingClientRect();
      const x = Math.max(0, Math.floor(r.x * scale)), y = Math.max(0, Math.floor(r.y * scale));
      const w = Math.max(1, Math.floor(r.width * scale)), h = Math.max(1, Math.floor(r.height * scale));
      const d = ctx.getImageData(x, y, w, h).data;
      const counts = new Map();
      for (let i = 0; i < d.length; i += 4) {
        const k = (d[i] >> 3) + "," + (d[i + 1] >> 3) + "," + (d[i + 2] >> 3);
        counts.set(k, (counts.get(k) || 0) + 1);
      }
      const [mr, mg, mb] = [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0].split(",").map((v) => Number(v) * 8 + 4);
      let ink = 0;
      for (let i = 0; i < d.length; i += 4)
        if (Math.abs(d[i] - mr) + Math.abs(d[i + 1] - mg) + Math.abs(d[i + 2] - mb) > 36) ink++;
      const share = ink / (w * h);
      if (share > 0.03) out.push(`label sits on a drawing (${Math.round(share * 100)}% of its box): "${t.textContent.trim().slice(0, 40)}"`);
    }
    return out;
  }, { bare, scale });
  report.problems.push(...onDrawing);
  await browser.close();
  if (report.minSize < 17) report.problems.push(`smallest label is ${report.minSize}px; use 17px or more so it stays readable on the blog`);
  const out = { ok: report.problems.length === 0, output, width: Math.round(W * scale), height: Math.round(H * scale),
    bytes: fs.statSync(output).size, labels: report.labels, min_font_px: report.minSize, problems: report.problems };
  out.md5 = require("crypto").createHash("md5").update(fs.readFileSync(output)).digest("hex");
  fs.writeFileSync(output.replace(/\.png$/, "") + ".report.json", JSON.stringify(out, null, 1) + "\n");
  console.log(JSON.stringify(out, null, 1));
  process.exit(out.ok ? 0 : 1);
})();
