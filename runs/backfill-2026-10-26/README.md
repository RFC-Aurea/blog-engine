# New images for the 14 engine posts published 2026-10-16 to 2026-10-26

Asked by Alifiya on 2026-10-26: the drawn beige infographics looked the same every day and their text was cut off in
the blog list. Each post gets a painted labelled medical illustration (IMAGE1, same place in the post) and a natural
photo (IMAGE2, replaces the old diagram and becomes the cover: `"hero": "IMAGE2"`). Style: `rules/images.md`.

`plan.json` lists, per post: the illustration subject, action, exact labels and alt text, the photo scene and alt text.
The prompts are already written to `runs/<run>/img/new/image1.prompt.txt` and `image2.prompt.txt`.

For each post in `plan.json` (needs `GEMINI_API_KEY`, or Gamma with `cdn.gamma.app` allowed):
1. `python3 scripts/gen_image.py runs/<run>/img/new/image1.prompt.txt runs/<run>/img/new/image1.jpg` and the same
   for image2.
2. Look at both with the Read tool. The illustration's labels must match `plan.json` letter for letter and point at
   the right parts; the photo must look real with no text. Fix the prompt and generate again if not (3 tries).
3. Move them to `runs/<run>/img/image1.jpg` / `image2.jpg` with their `.report.json` and `.prompt.txt` (keep the old
   `.png`/`.html` files), commit and push, upload both from commit-pinned raw URLs, confirm the Wix hash = md5.
4. Front matter: move the old `images` block into `replaced_images` (with today's date), write the new block
   (`generator`, `model`, `kind`, `source`, `file`, `width`, `height`, `md5`, `wix_id`, `wix_hash`, `alt`, `labels`,
   `reviewed`, `preview_src`) and set `"hero": "IMAGE2"`.
5. `python3 scripts/check_post.py runs/<run> --update <post_id>`, `python3 scripts/build_post.py runs/<run> --update <post_id>`,
   `node scripts/test_publish_js.js runs/<run>`, publish with `templates/publish.js` (CLAUDE.md step 10), save
   `live_summary.json`, `python3 scripts/verify_live.py runs/<run>`.
6. Add an `updated` row to `runs/log.md` ("new images: painted illustration + photo"), commit and push.

Progress is tracked in `progress.json` (one entry per run: `images_ok`, `live_ok`).
