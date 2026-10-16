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
Use the banner size preset. Generate, then **look at the image** (download it or view it) and reject it if it has any text-like marks, wrong anatomy, extra fingers, brand colours, or looks off-topic. Up to 2 retries per image; if both images still fail, the run stops for that topic (quality gate).

## Upload
1. Upload the accepted image URL to the brand's site with `mcp__Wix__UploadImageToWixSite` (`siteId` = brand site, `imageUrls` = [url], `displayName` = alt text shortened).
2. Record the returned media id (form `xxxxxx_...~mv2.png`, no `wix:image://v1/` prefix), width and height in the front matter `images` block. If width/height are not returned, read them with the Wix media API before building.

## Alt text
- Under 125 characters, describes what is shown, plain language.
- At least one of the two alt texts contains the primary keyword or a secondary keyword, naturally.
- No "image of" / "picture of".
