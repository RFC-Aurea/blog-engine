# Topic engine rules (diversity and keyword wins)

Goal: hundreds, then thousands, of distinct posts across the two blogs, each targeting a keyword we can realistically rank for, with no repeated topics or near-duplicate titles.

## Data
- `data/keywords_raw.json` — every keyword row ever pulled from Ubersuggest (keyword, volume, SD, CPC, intent, pillar, date). Append only.
- `data/topics.json` — clusters built from the raw pool by `scripts/build_topics.py`. One cluster = one future post = one primary keyword plus its close variants. Each cluster has an owner brand, a pillar, a suggested format, a score and a status (`available`, `used`, `blocked`).
- `data/published.json` — every post live on either blog (the 72 that existed on 2026-10-16 plus everything the engine publishes). Used for uniqueness checks and internal links.

## Pillars and ownership
| Pillar | Owner | Notes |
|---|---|---|
| low-amh-dor (low AMH, DOR, high FSH) | RFC | |
| poi (POI/POF, early menopause and pregnancy) | RFC | |
| rejuvenation (ovarian/uterine PRP, adipose-PRP, stem cells) | RFC | |
| ivf-over-40 (IVF, egg quality, pregnancy at 40–50) | RFC | |
| immunology-rpl (recurrent loss, implantation failure, NK cells, chronic endometritis) | RFC | Aurea may write an under-40 angle only if RFC hasn't used the cluster |
| donor-surrogacy | RFC | |
| perimenopause-sexual (perimenopause, hormones, vaginal/sexual health) | RFC | |
| pcos-bmi (PCOS, plus-size IVF, no BMI cutoff) | RFC | |
| gentle-ivf (natural, mini, low-stim IVF) | RFC | Aurea writes protocol-choice angles under ivf-protocols |
| egg-freezing (under 38) | Aurea | Aurea already has ~8; new posts must take an unused angle (number of eggs, cycles, age data, thaw, travel, cost) |
| ivf-protocols (IVF under 40, process, timeline, retrieval, protocol choice) | Aurea | |
| cost-insurance (IVF/egg freezing prices, insurance, mandates, financing, refund programs) | Aurea | |
| embryology-lab (grading, PGT-A, FET, time-lapse, AI in the lab) | Aurea | |
| male-factor (semen analysis, sperm DNA, freezing, varicocele) | Aurea | |
| tubes-uterus-iui (HSG, blocked tubes, hydrosalpinx, polyps, lining, IUI) | Aurea | |
| oncofertility (fertility preservation, breast-safe IVF, BRCA) | Aurea | |
| endometriosis | split | RFC: endometriosis with recurrent failure/over 40/immunology. Aurea: under 40, surgery vs IVF, endo-specific protocols |
| lifestyle-supplements | split | RFC: over 35/40 egg quality, Rejoova. Aurea: preconception for under 40, male partner |
| conception-basics (ovulation, TTC timing) | split | Aurea by default; RFC when the keyword mentions 35+/40+/perimenopause |
| hormones-conditions (thyroid, prolactin, GLP-1, vitamin D) | split | GLP-1/PCOS: RFC if plus-size angle, Aurea otherwise |
| pregnancy-loss (chemical pregnancy, blighted ovum) | split | RFC owns recurrent; Aurea owns first-time loss after IVF |

A "shared"/split cluster is assigned to one brand when it is picked and is then used up for both brands.

## Scoring (scripts/build_topics.py)
score (0–100) = volume points (0–40, log scale; 10/mo ≈ 10, 100 ≈ 20, 1,000 ≈ 30, 10,000 ≈ 40) + difficulty points (0–30; SD 0 = 30, SD 60+ = 0) + intent/service fit (0–20; informational question or treatment keyword tied to a brand service scores highest) + CPC signal (0–10; CPC shows commercial value).
Prefer SD under 30 and volume 50+; clusters under 20/mo total are kept but rank low. Cluster volume = sum of member keywords' volumes (a post ranks for its variants too).

## Hard rules (scripts/pick_topic.py enforces)
1. A cluster is used once, ever. After publishing, `scripts/record.py` marks it `used` and adds its keywords to the used list.
2. Uniqueness: the cluster's primary keyword and the drafted title are compared against every title and slug in `data/published.json` (both brands). Block if word-overlap similarity ≥ 0.6, or if the primary keyword's core words all appear in an existing title.
3. A brand never repeats a pillar within its last 4 posts.
4. Format and title shape rotation per rules/formats.md.
5. About 1 in 4 posts comes from a "what's new" slot: a recent study, guideline, drug approval or news item (found by web search), **only if** Ubersuggest `keyword_overview` shows real volume (≥ 30/mo) for the keyword it maps to. Buzz without volume is skipped.
6. Before writing, confirm the picked keyword with `keyword_overview` (fresh volume + SD) and `serp_analysis` (who ranks, what they miss → the content-gap H2). If SD now ≥ 45 or volume is 0, mark the cluster `blocked` and take the next one.

## Growing the pool (every run)
Each run spends up to ~10 extra Ubersuggest reports on expansion: `keyword_suggestions` on 2–3 new seeds taken from the current post's secondary keywords and People Also Ask questions, appended to `data/keywords_raw.json`, then `scripts/build_topics.py` is re-run. At ~30 posts a month this grows the pool by several hundred keywords a month while staying far inside the 150-reports/day limit.
