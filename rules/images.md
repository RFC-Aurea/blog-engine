# Image rules (2 per post)

Set by Alifiya on 2026-10-26: **IMAGE1 is a research-grade medical illustration drawn by Claude; IMAGE2 is a real-looking
Gamma photo and is the cover** (`"hero": "IMAGE2"`). She rejected image-model illustrations (Gamma's anatomy was
cartoonish and wrong) and the old beige infographics (same look every day, text cut off in the blog list).

## IMAGE1: Claude-drawn medical illustration (`generator: "drawn"`)
**The look.** Like a figure in a medical textbook or journal: anatomically correct, drawn cell by cell where cells
matter, rendered with depth, **white background**, **medical colours** (rose-pink muscle, deeper red-pink lining,
cream-salmon ovarian stroma, golden granulosa cells and follicle fluid, cream egg cytoplasm, lilac-white zona, purple
nuclei and chromosomes, red arteries, blue veins, straw-yellow plasma). **Never brand colours** (no RFC #09332C or
#F0531C, no Aurea #BB2423 or #FF64BA). Labels in journal style (dark grey, fine leader lines ending exactly on the part,
panel letters A/B when there are two panels). No banner title inside the image. Not the same subject or composition
as the brand's last 2 posts (look at `runs/*-<brand>/img/figure1.png`).

**How.** Parts come from the library `illustrations/medical.svg` (built by `python3 illustrations/build_medical.py`
from `illustrations/medlib/`). Catalogue with every part's viewBox, what it shows and its named anchor points:
`illustrations/medical_parts.json` (or `python3 scripts/figure.py --anchors <part>`). Parts today: ovary sections
(`m-ovary-section`, `m-ovary-cortex-prp`, `m-ovary-poi`, `m-ovary-pcos`, `m-ovary-stimulated`), follicles at each stage
(`m-follicle-primordial|primary|secondary|antral`), `m-egg-mii` / `m-egg-mii-bare` (spindle, chromosomes, polar body),
`m-blastocyst`, `m-blastocyst-hatching`, karyotypes (`m-karyotype`, `-xy`, `-trisomy21`), DNA (`m-dna`,
`m-dna-broken`), instruments (`m-needle`, `m-syringe`, `m-holding-pipette`, `m-biopsy-pipette`, `m-prp-tube`,
`m-prp-cloud`, `m-us-probe`), sperm (`m-sperm`, `m-sperm-plain`, `m-sperm-head-dna`, `m-sperm-head-dna-broken`),
whole reproductive tract (`m-tract`, `m-tract-hsg` with catheter and dye, `m-tract-transfer` with transfer catheter)
and whatever later runs added (always check the catalogue).

1. Write `RUN/img/figure1.json` (format in the docstring of `scripts/figure.py`): place parts (`x`/`y`/`width`, or
   `pin` an anchor to a canvas point, `rotate`, `flip`), labels with `to` = `<part name>.<anchor>` so each leader line
   ends on the named structure, panel letters. Canvas 1200x630. Labels go on white space around the drawing.
   Past specs to copy from: `runs/*/img/figure1.json`.
2. `python3 scripts/figure.py RUN/img/figure1.json` (writes `figure1.html`), then
   `node scripts/render_image.js RUN/img/figure1.html RUN/img/figure1.png` (1800x945). Exit code 1 = a label problem
   (overlap, outside the canvas, under 17px, or sitting on the drawing): fix the spec.
3. Look at the PNG with the Read tool (and crops at full size) and fix until it is right: anatomy correct, nothing cut
   off at the edges, every leader ending on the right part.
4. **A missing part** (for example a uterus, sperm, testis or endometrium close-up): add it to `illustrations/medlib/`
   in the same style (cells via `packed_cells`/`cell_layer`, gradients from `defs.py`, anchors for labels), rebuild,
   look at it alone first, and say so in the run report. Do not fall back to flat icons.
5. Front matter: `generator` `drawn`, `kind` `medical illustration`, `source` `img/figure1.html`, `file`
   `img/figure1.png`, width 1800, height 945, `md5`, `wix_id`, `wix_hash`, `alt`, `labels` (every visible word),
   `reviewed` true, `preview_src` `img/figure1.png`.

## IMAGE2: Gamma photo, the cover (`generator: "gamma"`)
1. `python3 scripts/fetch_image.py --check`. Exit 4 = cdn.gamma.app is blocked here: do not spend credits; draw a second
   illustration as IMAGE2 instead (a different subject, label-free and centred so it works as the cover) and say so in
   the report.
2. Write the prompt to `RUN/img/photo.prompt.txt` from this template (fill the scene from the post):
   "Natural editorial photograph for a fertility clinic blog: [scene]. Soft daylight, real textures, gentle shallow
   depth of field, warm natural colours, white and light wood surroundings. Realistic, not staged or glossy. No text,
   logos or readable screens; no babies, pregnant bellies, needles or blood. Landscape 16:9, subject centred."
   Adults only; never presented as clinic staff or patients; never a doctor who could pass for Dr. Merhi. Not the
   same scene as the brand's last 2 photos.
3. `mcp__Gamma__generate_image` (`type` `photo`, `sizePreset` `banner`), poll `mcp__Gamma__get_image_generation_status`,
   then `python3 scripts/fetch_image.py <url> RUN/img/photo.jpg --prompt RUN/img/photo.prompt.txt --credits <left>`.
4. Look at it with Read: it must look like a real photo, with no text, no warped hands or faces, subject in the middle
   (the blog list crops the sides to a near-square card). Up to 3 tries.
5. Front matter: `generator` `gamma`, `kind` `photo`, `source` `img/photo.prompt.txt`, `file` `img/photo.jpg`, width and
   height from `photo.report.json`, `md5`, `wix_id`, `wix_hash`, `alt`, `labels` [], `reviewed` true, `preview_src`,
   `gamma_url`. About 70 credits per photo; report credits left.

## Content rules (the checker enforces the starred ones)
Every word must be true and match the post. **\*Every number in an image must appear in the post body.** **\*Same
banned words and brand claim rules as the post.** No logos, watermarks or clinic names. Anatomy oriented normally
(uterus fundus up; sperm head first). No faces in illustrations, no blood spills, babies or pregnant bellies.

## Upload (both images)
1. Commit and push the run folder (the repo is public):
   `git add RUN && git -c user.name="Blog Engine" -c user.email="noreply@anthropic.com" commit -m "<brand>: images" && git push origin HEAD:main`.
2. `mcp__Wix__UploadImageToWixSite` (`siteId` = brand site) with **commit-pinned** raw URLs:
   `https://raw.githubusercontent.com/RFC-Aurea/blog-engine/<git rev-parse HEAD>/RUN/img/<file>`.
3. Confirm with `mcp__Wix__ExecuteWixAPI` (read-only):
   `POST https://www.wixapis.com/site-media/v1/files/get-files` `{"fileIds": [<id1>, <id2>]}`
   (docs: https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/get-file-descriptors).
   Each must be `READY` with the file's width and height, and its `hash` must equal the file's md5. If `PENDING`, read
   again.
4. Record `wix_id` and `wix_hash` in the front matter.

If an upload fails, the topic is blocked with the reason "image upload failed"; do not publish without both images.

## Alt text
- Under 125 characters, says what the image shows ("Labelled illustration of ...", "A woman and her doctor ...").
- At least one of the two alt texts contains the primary keyword or a secondary keyword, naturally.
- No "image of" / "picture of" / "photo of".
