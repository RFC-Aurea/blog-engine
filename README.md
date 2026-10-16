# RFC + Aurea blog engine

Publishes one fully researched, SEO and GEO optimised post per day, alternating between
rejuvenatingfertility.com and aureafertility.com (each site every other day). Runs as a scheduled Claude task on the
Max plan, using the Wix and Ubersuggest connections on the Claude account. No API keys are stored here.

**What every post gets:** a trending keyword with real Ubersuggest volume and difficulty; title as H1 and H2/H3
structure; a clickable table of contents linking to every H2; inline links to verified research papers; 8+ internal
links; 2 labelled illustrations in neutral colours (drawn in code, rendered with Chromium) with alt text; Wix SEO title, description, main keyword and schema (MedicalWebPage +
FAQ); brand-coloured headings; Dr. Merhi as writer. A quality gate blocks anything that fails.

**Topic diversity:** a keyword pool clustered into topics, each topic used once and owned by one brand, with pillar,
format (12 types) and title-shape rotation and a similarity check against every existing post on both blogs.

| Path | What it is |
|---|---|
| `CLAUDE.md` | The daily run, step by step (what the scheduled task follows) |
| `config.json` | Sites, writer, categories, brand colours, limits, **pause switch** |
| `brands/` | RFC and Aurea voice, claims rules, verified internal links, pillars |
| `rules/` | Writing/SEO/GEO rules, the 12 formats and title shapes, image rules, topic rules |
| `data/published.json` | Every live post (used for uniqueness and internal links) |
| `data/keywords_raw.json`, `data/topics.json` | Keyword pool and topic clusters |
| `illustrations/` | Shared style and part library (uterus, ovary, egg, sperm, embryo, lab tools, icons) for the images |
| `scripts/` | Topic picker, post builder (markdown → Wix rich content), image renderer, quality checker, verifier, ledger |
| `runs/` | One folder per day with research, evidence, the post source, checks and the live result; `runs/log.md` |

**Pause:** set `"paused": true` in `config.json`. **Change colours, categories or limits:** edit `config.json`.
