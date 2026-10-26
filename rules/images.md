# Image rules (2 per post)

## The look (Alifiya, 2026-10-26)
- **White background and natural colours** for medical illustrations: soft coral and pink tissue, cream follicles and
  cells, muted teal for fluids, warm grey lines. **Never brand colours** (no RFC deep green #09332C or orange #F0531C,
  no Aurea red #BB2423 or pink #FF64BA as a dominant colour). Her reference:
  `illustrations/reference/alifiya-example-ovarian-prp.jpg` (painted ovary cross-section, fine leader lines, thin
  grey labels, small legend, lots of white space). Look at it with the Read tool before writing a prompt.
- **Not the same every day.** The two images can be any mix of:
  - a **labelled medical illustration** (anatomy, cells or how the treatment works), painted like the reference;
  - a **natural photo** (real-looking, editorial: a calm consultation, hands holding a cup or a calendar, an
    ultrasound room, a lab bench, a couple walking, a pharmacy shelf; whatever fits the post);
  - a **labelled diagram** (timeline, cost breakdown, comparison) when the post's own numbers or steps are the point.
  Default: IMAGE1 = labelled medical illustration where the post explains how it works or the research, IMAGE2 =
  natural photo near the next steps, and `"hero": "IMAGE2"` so the photo is the cover. Two illustrations when the
  topic is mostly anatomy or a procedure. Before choosing, look at the last 2 posts of the same brand
  (`runs/*-<brand>/img/`) and do not repeat their subject, composition or setting.
- **Cover (`hero` in the front matter):** the blog list crops the sides of the cover to a near-square card, so the
  cover has **no title or other text** and its subject sits in the middle. A photo or a label-free illustration.
- **Content rules (the checker enforces the starred ones).** Every word must be true and match the post.
  **\*Every number in an image must appear in the post body** (painted images: avoid numbers; put numbers in a drawn
  diagram). **\*Same banned words and brand claim rules as the post.** No logos, watermarks or clinic names (except a
  drawn price diagram that names the clinic's own prices). Anatomy correct and oriented normally (uterus fundus up,
  cervix down; sperm head first; blastocyst inner cell mass on one side).
- **Photos:** adults only, shown naturally and diverse; never presented as the clinic's own patients or staff, never
  a doctor who could pass for Dr. Merhi. No babies, pregnant bellies, needles into skin, blood or distress. No text
  on objects (screens, papers and labels blank or blurred).

## How images are made
Use the first route that is available; record it as `generator` in the front matter.

### 1. Gamma (`generator: "gamma"`), chosen by Alifiya 2026-10-26
1. `python3 scripts/fetch_image.py --check`. Exit code 4 = this environment cannot download from `cdn.gamma.app`:
   do not spend credits, use route 2 for both images and say so in the run report.
2. Write the prompt to `RUN/img/imageN.prompt.txt` from the templates below.
3. `mcp__Gamma__generate_image` with that prompt, `type` `illustration` (medical illustration) or `photo`, and
   `sizePreset` `banner`. Poll `mcp__Gamma__get_image_generation_status` every few seconds until `completed` (never
   call generate_image again to check). Note `credits.remaining` from the result.
4. `python3 scripts/fetch_image.py <image url> RUN/img/imageN.jpg --prompt RUN/img/imageN.prompt.txt --credits <remaining>`
   (saves an 1800 px wide JPEG and `imageN.report.json`).
5. **Look at the JPEG with the Read tool.** Check every label letter by letter against your list, that each leader
   line points at the part it names, the anatomy, no stray or garbled text, white background, no brand colours, and for
   photos: real-looking hands, faces and objects. If anything is wrong, change the prompt and generate again (at most
   3 tries per image, about 70 credits each). Still wrong: draw that image instead (route 2).
6. Push, upload and confirm as in "Upload" below. Front matter: `generator`, `kind` (`medical illustration`,
   `photo` or `labelled diagram`), `source` (`img/imageN.prompt.txt`), `file` (`img/imageN.jpg`), `width`/`height`
   (from the report), `md5`, `wix_hash`, `alt`, `labels` (every word visible in the image, exactly as shown; `[]` for
   a photo), `reviewed: true`, `preview_src` (= `file`), `gamma_url`.

**Illustration prompt template** (fill the brackets; list every label):
```
Medical illustration for a patient education blog, in the style of a modern textbook plate: [subject, e.g. a human
ovary in cross-section with follicles at different stages], [what is happening, e.g. a thin needle delivering
platelet-rich plasma into the ovarian tissue]. Pure white background, plenty of white space. Natural colours only:
soft coral and pink tissue, cream cells, muted teal for fluids, warm grey outlines; delicate linework with gentle
painted shading and a soft glow where something is active. Anatomically accurate. Labels in a thin dark-grey
sans-serif font with fine grey leader lines pointing exactly at each part, spelled exactly: "[label 1]", "[label 2]",
... No other text, no title, no numbers, no logos, no watermark. Avoid dark green, bright orange, red and hot pink.
Landscape 16:9.
```
For a cover illustration drop the labels and say "no text at all".

**Photo prompt template:**
```
Natural editorial photograph for a fertility clinic blog: [scene, e.g. a woman in her early 40s and her partner
talking with a doctor in a bright, calm consultation room, seen from the side, faces relaxed]. Soft daylight, real
textures, gentle shallow depth of field, warm natural colours, white and light wood surroundings. Realistic, not
staged or glossy. No text, logos or readable screens; no babies, pregnant bellies, needles or blood. Landscape 16:9,
subject centred.
```

### 2. Drawn in code (`generator: "drawn"`), the fallback and the route for number-heavy diagrams
SVG in `RUN/img/imageN.html` using `{{BASE_CSS}}` (`illustrations/base.css`: white background, natural colours) and
`{{COMPONENTS}}` (`illustrations/components.svg` parts). Copy the closest past `image*.html` from `runs/` and change
the layout, do not reuse it unchanged.
- Canvas `<svg class="canvas" viewBox="0 0 1200 630">`, rendered at 1.5x = 1800x945 PNG:
  `node scripts/render_image.js RUN/img/imageN.html RUN/img/imageN.png` (exit code 1 = a label problem: fix it).
- Classes: `title`, `subtitle`, `card`, `step-title`, `step-text`, `label`, `label-sub`, `big-number`, `note`,
  `badge`/`badge-num`, `leader`/`leader-dot`, `arrow-solid` + `m-arrow`; accents `teal`, `teal-soft`, `coral`,
  `coral-soft`.
- Parts (`<use href="#name" x y width height/>`): `uterus`, `uterus-body`, `ovary-section`, `ovary-poi`, `oocyte`,
  `sperm`, `sperm-detail`, `blastocyst`, `holding-pipette`, `icsi-needle`, `catheter`, and 48x48 icons
  (`icon-clipboard`, `icon-profile`, `icon-calendar`, `icon-dish`, `icon-uterus`, `icon-drop`, `icon-check`,
  `icon-cup`, `icon-vial`, `icon-tank`, `icon-phone`, `icon-microscope`, `icon-snowflake`, `icon-thaw`).
  A point (vx, vy) in a symbol's viewBox lands at x + (vx - minX) * width / vbWidth. A missing part: add a new
  `<symbol>` in the same style and say so in the run report.
- Labels 17px or larger; **\*no label may overlap another, run into a drawing, leave its card or the canvas**.
- Look at the PNG with the Read tool and fix until it is right. Front matter as in route 1 with `generator` `drawn`, `source`
  `img/imageN.html`, `file` `img/imageN.png`, width 1800, height 945 (`labels`/`reviewed` not needed).

## Upload (all routes)
1. Commit and push the run folder so the files are on GitHub (the repo is public):
   `git add RUN && git -c user.name="Blog Engine" -c user.email="noreply@anthropic.com" commit -m "<brand>: images" && git push origin HEAD:main`.
2. `mcp__Wix__UploadImageToWixSite` (`siteId` = brand site) with **commit-pinned** raw URLs, which are never stale:
   `https://raw.githubusercontent.com/RFC-Aurea/blog-engine/<git rev-parse HEAD>/RUN/img/imageN.<jpg|png>`.
3. Confirm with `mcp__Wix__ExecuteWixAPI` (read-only):
   `POST https://www.wixapis.com/site-media/v1/files/get-files` `{"fileIds": [<id1>, <id2>]}`
   (docs: https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/get-file-descriptors).
   Each must be `READY` with the file's width and height, and its `hash` must equal the file's md5
   (`md5sum RUN/img/imageN.*`): that proves Wix holds exactly the picture you reviewed. If `PENDING`, read again.
4. Record `wix_id` and `wix_hash` in the front matter.

If an upload fails (for example the repo was made private and Wix cannot fetch the URL), the topic is blocked
with the reason "image upload failed" and the run report says so; do not publish without both images.

## Alt text
- Under 125 characters, says what the image shows in plain language ("Labelled illustration of ...",
  "A woman and her doctor ...", "Timeline of ...").
- At least one of the two alt texts contains the primary keyword or a secondary keyword, naturally.
- No "image of" / "picture of" / "photo of".
