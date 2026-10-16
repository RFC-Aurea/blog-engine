# Image rules (2 per post)

## What to make
- **IMAGE1** (research section): visualises the mechanism, anatomy, cell biology or the main comparison. Usually a **medical illustration**.
- **IMAGE2** (next-steps section): visualises the process, timeline, clinic step or the human side. Medical illustration **or** a calm editorial scene/photo, decided by topic:
  - anatomy, hormones, cells, lab, procedures, test results → medical illustration;
  - costs, decisions, lifestyle, emotions, consultation, planning → editorial scene (real-looking people, clinic or home setting).
- IMAGE1 is also the cover (hero) image unless IMAGE2 is clearly more inviting for the blog list; set `"hero"` in the front matter.

## Style (both brands)
- **Neutral colours only. No brand colours inside images** (no RFC green/orange, no Aurea red/pink, no logos).
- Palette per brand from `config.json → image_palette` (RFC: ivory, warm sand, soft stone grey, muted sage; Aurea: ivory, champagne, warm taupe, soft lilac grey).
- Clean, modern, editorial; soft light; generous negative space; landscape 16:9 / banner.
- **No text, letters, numbers, labels, watermarks or logos in the image** (AI image models misspell text). Labels belong in the article, not the picture.
- Medical accuracy: correct anatomy (ovary, follicles, uterus, tubes, endometrium, sperm, embryo stages). No gore, no needles into skin close-ups, no pregnant-belly clichés, no babies unless the topic is birth outcomes.
- People: diverse adults, natural expressions, modest clothing; no identifiable real people; no children.

## Prompt template (Gamma `generate_image`)
`[subject + viewpoint], [style: clean vector medical illustration | soft editorial photograph], palette of [brand palette], plain [ivory] background, soft even lighting, minimal, high detail, no text, no labels, no letters, no logos, no watermark.`
Use the banner size preset (Gamma returns 2752x1536).

**Checking the result.** The sandbox cannot open Gamma or Wix image URLs (the proxy blocks `cdn.gamma.app` and `static.wixstatic.com`), so you cannot look at the picture yourself. Instead:
1. Upload it (below), then read its file descriptor with `mcp__Wix__ExecuteWixAPI`:
   `POST https://www.wixapis.com/site-media/v1/files/get-files` with `{"fileIds": [<id>, <id>]}`
   (docs: https://dev.wix.com/docs/api-reference/assets/media/media-manager/files/get-file-descriptors).
2. Confirm `operationStatus` is `READY`, read `media.image.image.width/height`, and read Wix's automatic `labels`.
3. The labels must match the subject (an embryo illustration gets labels like "biomedical illustration", "embryo"; a
   consultation scene gets "counselling session", "consulting room"). Wix has no "sperm" label: microscopic subjects come
   back as "scientific micrograph", "microorganism", "human cell", even "bacterium", which is fine. Reject and regenerate
   if the labels name everyday objects or food the picture should not look like (e.g. "spoons", "flatware", "legume" for
   a sperm illustration), or mention text, signage, documents, logos or screens. Up to 2 retries per image; if an image still fails, the run
   stops for that topic (quality gate).
4. Copy the 4–6 most relevant labels into the front matter as `wix_labels` so the record shows what was checked.
Strict prompts (palette, "no text", subject) carry the rest; Alifiya reviews images on the live blog.

## Upload
1. Upload the accepted image URL to the brand's site with `mcp__Wix__UploadImageToWixSite` (`siteId` = brand site, `imageUrls` = [url], `displayName` = alt text shortened).
2. Record the returned media id (form `xxxxxx_...~mv2.jpg`, no `wix:image://v1/` prefix), width and height in the front matter `images` block. The upload result does not include width/height; take them from the file descriptor in the check above.

## Alt text
- Under 125 characters, describes what is shown, plain language.
- At least one of the two alt texts contains the primary keyword or a secondary keyword, naturally.
- No "image of" / "picture of".
