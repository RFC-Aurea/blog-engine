# Image rules (2 per post): labelled illustrations, drawn in code

Alifiya wants **medical illustrations with labels, like the clinics' own posts** (2026-10-16). AI image models
(Gamma included) cannot write labels reliably, so the engine draws each image itself as SVG inside an HTML file,
renders it to PNG with the sandbox's Chromium, **looks at the PNG** (Read tool), fixes what is wrong, and uploads
the exact file to Wix. Gamma is no longer used.

The clinics' existing posts set the pattern: one anatomical/mechanism illustration with labels and one labelled
diagram (timeline, workflow, comparison or cost breakdown). Examples from the live sites: "Medical illustration of
ovarian PRP injection showing subcapsular follicles and platelet growth factors", "Treatment timeline for chronic
endometritis antibiotics", "Blastocyst grading chart (Gardner system)".

## What to make
- **IMAGE1** (in or right after the research section): the mechanism, anatomy or cell biology behind the topic,
  with labels. Optionally a small data panel with 1–2 numbers from a cited study and its source line.
  Examples in this repo: `runs/2026-10-16-rfc/img/image1.html` (donor egg steps: ovary, ICSI, uterus),
  `runs/2026-10-16-aurea/img/image1.html` (sperm anatomy + motility before/after freezing).
- **IMAGE2** (in or right after next steps): a labelled timeline, workflow, comparison or cost diagram built from
  the post's own steps, tests and prices. Examples: `runs/2026-10-16-rfc/img/image2.html` (6-step timeline + tests
  to ask for), `runs/2026-10-16-aurea/img/image2.html` (5 steps with prices + 10-year total bar).
- IMAGE1 is the cover (hero) unless IMAGE2 is clearly more inviting.
- Copy the closest example and adapt it; do not start from a blank file.

## Content rules (the checker enforces the starred ones)
- Every word must be true and match the post. **\*Every number in the image (prices, %, days, study sizes) must
  appear in the post body.** Do not add facts the post does not make.
- **\*Same banned words and brand claim rules as the post** (no "journey", no unsupported Aurea claims, RFC hope-first).
- Title (34px) and one-line subtitle at the top, then 2–3 panels or a 4–6 step row. At most about 14 labels.
- Labels are short nouns or phrases ("Lining (endometrium)", "Soft catheter"), 17px or larger so they stay
  readable when the blog shrinks the image to ~740px wide. **\*No label may overlap another label, run into a
  drawing, run out of its card or off the canvas** (the renderer checks this).
- Leader lines (`class="leader"` + `leader-dot`) point exactly at the part named. Anatomy must be correct and
  oriented normally (uterus fundus up, cervix down; sperm head first; blastocyst inner cell mass on one side).
- Neutral palette only (ivory, sand, stone, taupe; natural tissue tones; muted sage for RFC or soft lilac grey for
  Aurea as a single accent). **No brand colours** (no RFC green/orange, no Aurea red/pink), no logos, no clinic names
  in the image except where the post itself names the clinic's own prices (e.g. "Sperm freezing at Aurea").
- No people, faces, needles into skin, blood, babies or pregnant bellies.

## Building blocks
- Canvas: `<svg class="canvas" viewBox="0 0 1200 630">`, rendered at 1.5x = **1800x945 PNG**.
- `{{BASE_CSS}}` (`illustrations/base.css`): classes `title`, `subtitle`, `card`, `step-title`, `step-text`,
  `label`, `label-sub`, `big-number`, `note`, `badge`/`badge-num`, `leader`/`leader-dot`, `arrow-solid` + `m-arrow`.
- `{{COMPONENTS}}` (`illustrations/components.svg`), used as `<use href="#name" x y width height/>`:
  anatomy and cells: `uterus` (with tubes and ovaries), `uterus-body`, `ovary-section`, `oocyte`, `sperm`,
  `sperm-detail`, `blastocyst`; lab: `holding-pipette`, `icsi-needle`, `catheter`; icons (48x48):
  `icon-clipboard`, `icon-profile`, `icon-calendar`, `icon-dish`, `icon-uterus`, `icon-drop`, `icon-check`,
  `icon-cup`, `icon-vial`, `icon-tank`, `icon-phone`, `icon-microscope`, `icon-snowflake`, `icon-thaw`.
  Read the symbol's viewBox to place labels: point (vx, vy) lands at x + (vx - minX) * width / vbWidth.
- A topic needs a part that does not exist yet (e.g. testis, fallopian tube close-up, follicle stages, endometrium
  layers)? Draw it as a new `<symbol>` in `illustrations/components.svg` in the same style (soft gradients from the
  defs, 1.5–2px warm outlines) so later posts can reuse it, and say so in the run report.

## Steps
1. Write `RUN/img/image1.html` and `RUN/img/image2.html`.
2. Render: `node scripts/render_image.js RUN/img/image1.html RUN/img/image1.png` (same for image2). It writes
   `imageN.report.json`; exit code 1 means a label problem: fix and re-render.
3. **Look at both PNGs with the Read tool.** Check anatomy, that every leader points at the right part, spelling,
   and that nothing looks cramped or empty. Fix and re-render until you would show it to Alifiya.
4. Commit and push the run folder so the PNGs are on GitHub (the repo is public):
   `git add RUN && git -c user.name="Blog Engine" -c user.email="noreply@anthropic.com" commit -m "<brand>: images" && git push origin HEAD:main`.
5. Upload with `mcp__Wix__UploadImageToWixSite` (`siteId` = brand site) using **commit-pinned** raw URLs, which are
   never stale: `https://raw.githubusercontent.com/RFC-Aurea/blog-engine/<git rev-parse HEAD>/RUN/img/imageN.png`.
6. Confirm with `mcp__Wix__ExecuteWixAPI` (read-only):
   `POST https://www.wixapis.com/site-media/v1/files/get-files` `{"fileIds": [<id1>, <id2>]}`
   (docs: https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/get-file-descriptors).
   Each must be `READY`, 1800x945, and its `hash` must equal the PNG's md5 (`md5sum RUN/img/imageN.png`):
   that proves Wix holds exactly the picture you reviewed. If still `PENDING`, read again.
7. Record each image in the front matter `images` block: `wix_id`, `width` 1800, `height` 945, `alt`, `kind`,
   `source` (`img/imageN.html`), `file` (`img/imageN.png`), `md5`, `wix_hash`, `preview_src` (= `file`).
   `wix_labels` (Wix's automatic labels) is optional now.

If the upload fails (for example the repo was made private and Wix cannot fetch the URL), the topic is blocked
with the reason "image upload failed" and the run report says so; do not publish without both images.

## Alt text
- Under 125 characters, says what the labelled image shows, plain language ("Labelled illustration of ...",
  "Timeline of ...").
- At least one of the two alt texts contains the primary keyword or a secondary keyword, naturally.
- No "image of" / "picture of".
