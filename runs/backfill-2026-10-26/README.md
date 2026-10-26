# New images for the 14 engine posts published 2026-10-16 to 2026-10-26

Asked by Alifiya on 2026-10-26. Final decision (her words: "claude medical illustration + gamma real images"):
IMAGE1 = research-grade medical illustration drawn by Claude (`img/figure1.json` -> `figure1.html` -> `figure1.png`,
`rules/images.md`), IMAGE2 = the Gamma photo, used as the cover (`"hero": "IMAGE2"`). Gamma's own illustrations were
rejected and are recorded under `replaced_images`.

Photos: the 5 posts redone first (16-aurea, 16-rfc, 17-aurea, 20-aurea, 21-rfc) keep `img/image2.jpg`; the other 9 use
`img/photo.jpg` (made 2026-10-26, reviewed). `plan.json` lists each post's illustration subject, labels and alt text.

Per post: write the figure spec, render and look at it, push, upload from the commit-pinned raw URL, confirm the Wix
hash equals the md5, swap IMAGE1 (and IMAGE2 to the photo where needed) in the front matter, then
`check_post.py --update`, `build_post.py --update`, `test_publish_js.js`, publish with `templates/publish.js`, save
`live_summary.json`, `verify_live.py`, and add an `updated` row to `runs/log.md`.
