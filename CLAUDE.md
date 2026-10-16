# Blog engine — daily run instructions

This repo publishes one SEO + GEO blog post per day to two Wix blogs, alternating brands:
Rejuvenating Fertility Center (RFC) and Aurea Fertility Center. Posts go **live automatically** (no drafts) once
every hard check passes. Writer is always Dr. Zaher Merhi. Owner: Alifiya (RFC Fertility).

If you were started by the daily schedule, do the run below from start to finish without asking anyone anything.
Every outside tool you need is a connector: Wix, Ubersuggest (`Uber_suggest_SEO`), plus WebSearch/WebFetch.
Images are drawn in code and rendered with the sandbox's Chromium (see `rules/images.md`).
`wixapis.com`, PubMed and the clinic sites are blocked for curl in this sandbox — use the connectors and
WebSearch/WebFetch, never curl them.

Read before writing: `config.json`, `brands/<brand>.md`, `rules/writing.md`, `rules/formats.md`,
`rules/images.md`, `rules/topics.md`.

## Setup (each scheduled run starts in a fresh session)
- If this repo is not checked out yet: attach it with the `add_repo` tool (owner `RFC-Aurea`, repo `blog-engine`,
  push access), then `git clone https://github.com/RFC-Aurea/blog-engine` and work inside it.
- `git checkout main && git pull origin main` before step 1, so you start from the latest topic ledger.
- Needs only `python3` (standard library), `node` and the pre-installed Playwright + Chromium (used by
  `scripts/render_image.js`). Nothing to install.

## The run

`RUN` = `runs/<YYYY-MM-DD>-<brand>` (New York date). Keep every intermediate file there.

1. **Pause switch.** `python3 scripts/pick_topic.py` — exit code 2 means `config.json` has `"paused": true`: stop and
   say "Engine paused, nothing published."
2. **Pick.** The same command prints today's brand and up to 5 candidate clusters (already filtered for pillar
   rotation, format rotation and similarity to existing posts). Take the first. Create `RUN/`.
3. **Confirm the keyword (Ubersuggest, locId 2840).** `keyword_overview` on the cluster's primary keyword and
   `serp_analysis` (limit 10). If volume is 0 or SD ≥ 45: `python3 scripts/record.py RUN blocked "<why>"`, take the next
   candidate (`--skip` the blocked id). Pick 2–3 secondary keywords from the cluster variants or a
   `keyword_suggestions` call, each with its real volume and SD. Save everything you used in `RUN/research.json`.
   Never invent or estimate a metric. If Ubersuggest is down, stop the run and report it.
4. **Gap and patient language.** Read the top 3 ranking pages (WebFetch) and People Also Ask / forum threads
   (WebSearch, e.g. `site:reddit.com <keyword>`). Write the content-gap question and 3–6 exact patient phrases into the
   front matter (`serp_gap`, `patient_phrases`).
5. **Evidence.** WebSearch restricted to `pubmed.ncbi.nlm.nih.gov` / `pmc.ncbi.nlm.nih.gov` (plus ASRM, ESHRE, ACOG,
   CDC, NIH for guidelines and statistics). WebFetch every paper you intend to cite and confirm the abstract supports
   the exact claim. Record 5–10 sources in `RUN/evidence.json` (see `templates/evidence.json`), `verified: true` only
   when you read the supporting sentence yourself.
6. **Write** `RUN/post.md`: JSON front matter (see `templates/front_matter.json`) + body in the dialect described in
   `rules/writing.md`, using the format and an allowed title shape from step 2. Brand voice and claims from the brand
   file. 2,000–2,800 words. Spacing between blocks is added by the builder; just separate blocks with a blank line.
7. **Images.** Follow `rules/images.md`: draw two labelled illustrations from the finished post (`RUN/img/image1.html`,
   `RUN/img/image2.html`), render them with `node scripts/render_image.js`, look at each PNG with the Read tool and fix
   until it is right, push them, upload them to the brand's site from their commit-pinned GitHub URL, confirm Wix's
   file hash equals the PNG's md5, and record them in the front matter.
8. **Quality gate.** `python3 scripts/check_post.py RUN`. Fix every FAIL and re-run (one rewrite round). If it still
   fails, `python3 scripts/record.py RUN blocked "<failures>"` and go back to step 2 with the next candidate. After 2
   blocked topics in one run, publish nothing and report why.
9. **Build.** `python3 scripts/build_post.py RUN` then `node scripts/test_publish_js.js RUN` — must print `MATCH`.
10. **Publish.** Call `mcp__Wix__ExecuteWixAPI` with:
    - `siteId`: the brand's `site_id` from `config.json`
    - `code`: the full contents of `templates/publish.js`, copied exactly
    - `files`: `=== FILE: compact.json ===` on the first line, then the full contents of `RUN/compact.json`
    - `hasMutations`: true
    - `sourceDocUrls`: `https://dev.wix.com/docs/api-reference/business-solutions/blog/draft-posts/create-draft-post`,
      `https://dev.wix.com/docs/api-reference/business-solutions/blog/posts-stats/get-post`,
      `https://dev.wix.com/docs/api-reference/business-solutions/blog/draft-posts/get-draft-post`
      (and `https://dev.wix.com/docs/api-reference/business-solutions/blog/draft-posts/update-draft-post` when updating)
    Save the returned object as `RUN/live_summary.json`.
11. **Verify.** `python3 scripts/verify_live.py RUN`. If it reports problems, fix them with the Wix connector (update
    the post) or, if the post is wrong in a way you cannot fix, unpublish it, and say so in the summary.
12. **Record.** `python3 scripts/record.py RUN published <postId> <url>`.
13. **Grow the pool.** Spend up to 10 Ubersuggest reports: `keyword_suggestions` on 2–3 new seeds from today's
    secondary keywords / PAA questions. Save kept rows (volume ≥ 30, copied exactly) to a JSON file and run
    `python3 scripts/add_keywords.py <file> --brand <brand|shared> --pillar <pillar> --seed "<seed>"`.
14. **Save state.** `git add -A && git -c user.name="Blog Engine" -c user.email="noreply@anthropic.com" commit -m "<brand>: <post title>" && git push origin HEAD:main`
    (on a rejected push: `git pull --rebase origin main`, then push again).
15. **Report** (final message, it is sent to Alifiya): brand, title, live URL, primary keyword with volume/SD, number of
    citations and internal links, word count, any warnings from the checker, topics blocked today and why.

## Fixing a post the engine already published
Only for posts in `data/published.json` with `"source": "engine"` (the builder refuses any other id). Edit
`RUN/post.md` (and the images if needed), then `python3 scripts/check_post.py RUN --update <postId>`,
`python3 scripts/build_post.py RUN --update <postId>`, `node scripts/test_publish_js.js RUN`, and step 10 with the same
`templates/publish.js`: it updates the post in place (same id and URL) and publishes the change. Then step 11.

## Rules that never bend
- Writer `memberId` is `ca222303-63a3-4819-a4dd-9d9b3d27c79c` on both sites (set by the builder). Never use
  `7c1ac72f-a1f3-4da0-bbaa-82d7423c002a`.
- Only cite sources you opened and verified. Only link internal pages listed in the brand file or live posts.
- No invented success rates. RFC hope-first voice and banned words; Aurea unsupported-claims list.
- Images are labelled illustrations in neutral colours, no brand colours, every number taken from the post.
  Post styling uses brand colours from `config.json`.
- Never publish if `check_post.py` fails. Never edit or delete posts that the engine did not create.
- To stop the engine: set `"paused": true` in `config.json` and push.
