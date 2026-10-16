# Writing rules (every post, both brands)

Based on the `rfc-blog-production` skill, minus OpenEvidence (not used here: evidence comes from verified PubMed/PMC papers, see "Evidence" below). Brand voice and claims come from `brands/<brand>.md`.

## Required deliverables (the checker blocks the post if any are missing)
1. Primary keyword with its real Ubersuggest volume and SEO difficulty (SD). Never invent metrics. If Ubersuggest fails, stop the run.
2. 2–3 secondary keywords, each with real Ubersuggest volume and SD.
3. Meta title, 60 characters max, primary keyword near the front.
4. Meta description, 155 characters max, primary keyword plus an emotional hook.
5. Excerpt (shows on the blog list), 300 characters max, plain sentence.
6. Two images with alt text under 125 characters; at least one alt text contains the primary or a secondary keyword (see rules/images.md).
7. Inline hyperlinked citations to real papers (minimum 4), each one verified (see Evidence).
8. JSON-LD (MedicalWebPage + FAQPage). The builder generates it from the post; you do not hand-write it.
9. A filled self-audit (`checks.json` written by `scripts/check_post.py`).

## Source file format (`runs/<date>-<brand>/post.md`)
The post is written in a small, strict markdown dialect that `scripts/build_post.py` turns into Wix rich content with brand colours, anchors and SEO data.

```
---
{ JSON front matter, see templates/front_matter.json }
---
**Quick answer:** 2–4 sentences that answer the core question, bold key terms, include the primary keyword.

[[TOC]]

## What Is X — and Why Does It Matter? {#what-is-x}
A paragraph with **bold**, *italic*, an internal link [egg freezing](https://www.rejuvenatingfertility.com/egg-freezing)
and a citation on the meaningful words ([Smith et al., Fertility and Sterility, 2023](https://pubmed.ncbi.nlm.nih.gov/12345678/)).

### A subheading
- bullet item
1. numbered item

| Column A | Column B | Column C |
|---|---|---|
| real data | real data | real data |

[[IMAGE1]]

> A short pull quote (optional).
```

Rules of the dialect:
- The post title is the H1 (Wix renders the title field as H1). Never write `# ` in the body.
- Every `## ` heading must end with `{#anchor-id}` (lowercase, hyphens, unique, 3–30 chars). `[[TOC]]` becomes the clickable contents list linking to every H2, in brand colours.
- `### ` and `#### ` headings have no anchor.
- `[[IMAGE1]]` and `[[IMAGE2]]` place the two images; their Wix ids and alt text live in the front matter.
- Paragraphs are separated by a blank line. One paragraph = 2–4 sentences.
- Links: external links open in a new tab; links to the brand's own domain open in the same tab.
- No raw HTML, no footnotes, no reference list at the end.

## Structure (follow the format chosen in rules/formats.md)
Every format keeps these fixed parts, in this order:
1. **Quick answer** paragraph directly under the title (featured-snippet bait; for RFC it opens with what is possible).
2. `[[TOC]]`.
3. The format's body sections (from rules/formats.md). Across them the post must include:
   - an opening section that uses 1–2 real patient phrases (from Reddit/forums/People Also Ask research) so the reader feels seen, then explains the mechanism in plain words;
   - a "What the research shows" section with inline citations and a comparison table of 3+ columns with real numbers from the cited papers; IMAGE1 goes in or right after this section;
   - a dedicated H2 answering the content-gap question (the question the current top results do not answer);
   - a practical next-steps section (costs if known from the brand file, timeline, tests to ask for, questions for the doctor); IMAGE2 goes in or right after it.
4. `## Frequently Asked Questions {#faq}` with 5–6 questions, each an `### ` heading ending in `?`, answer 2–4 sentences. The primary keyword appears in at least one question. Questions come from People Also Ask, Ubersuggest question keywords and real patient wording.
5. `## The Bottom Line {#bottom-line}`: 2–3 warm sentences with one bolded key sentence.
6. CTA paragraph: 2–3 sentences, warm, names the clinic, links the brand's CTA URL (see brand file).

## SEO and GEO rules
- Primary keyword in: title (H1), Quick answer, first 100 words, at least 2 H2s, meta title, meta description, at least 1 FAQ question, at least 1 image alt text. Density about 1–1.5%; never stuffed.
- Secondary keywords in H2/H3s, body and alt text, naturally.
- Internal links: 8–12 minimum, from the brand file's verified pages and the brand's live posts in `data/published.json`. Link each service on first mention. Never invent a URL. Cross-link the sister clinic when routing applies.
- GEO (being quoted by AI answers): every H2 opens with a one- or two-sentence direct answer before detail; use concrete numbers with their source; name entities fully on first use (e.g. "anti-Müllerian hormone (AMH)"); write FAQ answers that stand alone; include one table and at least one numbered process list; date-stamp time-sensitive facts ("as of 2026").
- Length: 2,000–2,800 words of body text.
- Readability: grade 8–10, short sentences, short paragraphs, "you" and "your", every clinical term explained on first use.

## Evidence (replaces OpenEvidence)
- Find papers with web search restricted to `pubmed.ncbi.nlm.nih.gov` and `pmc.ncbi.nlm.nih.gov` (plus journal sites, ASRM, ESHRE, ACOG, CDC, NIH for guidelines and statistics).
- PubMed abstract pages often answer WebFetch with a captcha or a rate limit. Open the free full text on `pmc.ncbi.nlm.nih.gov` instead and cite that PMC URL; if PMC is also refusing, wait and try another paper. Never cite a page you could not read.
- For every paper you cite: open it (WebFetch) and confirm the abstract supports the exact claim and number you are writing. Record it in `evidence.json` (`url`, `title`, `year`, `claim`, `quote` copied from the abstract).
- Cite inline on the meaningful words: `([Author et al., Journal, Year](https://pubmed.ncbi.nlm.nih.gov/PMID/))` or `a [2024 cohort study in Human Reproduction](https://...) found…`. Never on "click here", never a bare URL, never a footnote.
- Only cite URLs present in `evidence.json`; the checker blocks any external research link that is not there. Never fabricate a PMID or DOI. If you cannot verify a claim, drop the claim.
- Prefer papers from the last 10 years, meta-analyses, RCTs, large cohorts and society guidelines.

## Banned words (checker enforces; applies to both brands)
game-changer, groundbreaking, revolutionary, in today's world, dive into, journey (as a noun), landscape, it's important to note, comprehensive, crucial, delve, navigate, realm, cutting-edge, pivotal, foster, leverage, robust, streamline, moreover, furthermore, it's worth noting, unlock, empower, embark, testament, tapestry, holistic approach, at the end of the day, in conclusion.
RFC adds its own list (brands/rfc.md). Aurea adds its unsupported-claims list (brands/aurea.md).

## Medical safety
- Educational tone: no individual diagnosis or dosing instructions. Medication names and typical protocols are fine when cited.
- No promises of pregnancy or live birth. No invented clinic success rates.
- When guidance differs between societies, say so and cite both.
