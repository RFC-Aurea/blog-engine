# Image rules (2 per post)

## The look (Alifiya, 2026-10-26)
- **Research-grade medical illustrations**, like the figures in a medical textbook or journal: anatomically exact,
  rendered with depth (shading, tissue texture), **white background**, **medical colours** (rose-pink myometrium,
  deeper red-pink endometrium, pale pink mucosa, cream-yellow follicles, red arteries, blue veins, yellow fat, purple
  nuclei and chromosomes). **Never brand colours** (no RFC deep green #09332C or orange #F0531C, no Aurea red #BB2423
  or pink #FF64BA). No cartoon or flat-infographic look, no beige cards.
- **Two illustrations per post, both drawn by Claude**: IMAGE1 = the anatomy or mechanism the post explains;
  IMAGE2 = a second figure (the procedure, a close-up such as a follicle, egg, embryo or sperm, or a labelled
  comparison). Not the same subject or composition as the brand's last 2 posts (`runs/*-<brand>/img/`).
- **Labels** like a journal figure: thin dark-grey sans-serif, fine leader lines ending exactly on the part named,
  panel letters (A, B) when there are two panels. No banner title inside the image.
- **Cover (`hero`)**: the blog list crops the sides of the cover to a near-square card, so the cover is the
  label-free version of IMAGE1 with its subject in the middle.
- **Content rules (the checker enforces the starred ones).** Every word must be true and match the post.
  **\*Every number in an image must appear in the post body.** **\*Same banned words and brand claim rules as the
  post.** No logos, watermarks or clinic names. Anatomy oriented normally (uterus fundus up, cervix down; sperm head
  first; blastocyst inner cell mass on one side). No people, faces, blood spills, babies or pregnant bellies.

## How images are made
**Every image is drawn by Claude in code** (Alifiya, 2026-10-26: she rejected Gamma's images and asked for
research-grade medical illustrations with medical colours on a white background, made by Claude). Do not use Gamma,
Gemini or any other image model, and no photos. Record `generator: "drawn"` in the front matter.

### Drawn in code (`generator: "drawn"`)
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
- Look at the PNG with the Read tool and fix until it is right. Front matter: `generator` `drawn`, `kind`, `alt`, `source`
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
