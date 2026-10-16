# Post formats and title shapes (rotation)

Every post uses one **format** (its body skeleton) and one **title shape**. `scripts/pick_topic.py` suggests both; the rules:
- The same format is never used twice in a row for a brand, and not more than twice in a brand's last 8 posts.
- The same title shape is not used in a brand's last 6 posts.
- The topic's search intent decides the format first (a "vs" keyword gets `comparison`, a cost keyword gets `cost-breakdown`, a "can I / does" question gets `straight-answer`, a number/test keyword gets `number-explained`).

Fixed parts of every format (see rules/writing.md): Quick answer → `[[TOC]]` → body below → FAQ (5–6) → Bottom line → CTA. Each body must still contain a research section with a 3+ column table, a content-gap H2, a practical next-steps section, IMAGE1 near the research and IMAGE2 near next steps. H2 count: 6–9 including FAQ and Bottom line.

## The 12 formats

1. **deep-guide** — the classic skill layout.
   H2s: What is X and why it matters → Why patients ask about X (3–4 H3 reasons) → How X works / the process → What the research shows → [content-gap question] → X vs. [alternative]: how to decide → What to expect: costs, timeline, next steps.

2. **comparison** — "X vs. Y".
   H2s: The short verdict (table up top) → How X works → How Y works → Head-to-head: what the research shows → Who each one suits (bullets per option) → [content-gap question] → Cost and timeline side by side.

3. **numbered-list** — "N causes / signs / options / mistakes".
   H2s grouped by theme, each with 2–4 numbered H3 items (e.g. "Causes you can test for" with H3 1–3, "Causes standard testing misses" with H3 4–7) → What the research shows → [content-gap question] → What to do next.

4. **straight-answer** — a yes/no or "can I" question.
   H2s: The short answer → When the answer is yes → When it's harder, and what helps (pair every obstacle with a treatment) → What the research shows → [content-gap question] → Your options, step by step.

5. **myth-vs-fact** — 6–8 myths.
   H2s: Why the myths stick → Myths about [A] (H3 per myth, each "Myth: … / Fact: …") → Myths about [B] → What the research actually shows → [content-gap question] → What to do with the facts.

6. **step-by-step** — a process or timeline ("week by week", "first visit to transfer").
   H2s: The whole timeline at a glance (numbered list + table) → Stage 1 → Stage 2 → Stage 3 (each stage: what happens, how long, what you feel) → What the research shows about [stage choice] → [content-gap question] → How to prepare.

7. **number-explained** — a test result or number ("AMH of 0.5", "FSH 15", "endometrial thickness 6 mm").
   H2s: What the number measures → Ranges by age (table) → What it predicts and what it doesn't → What the research shows → [content-gap question] → Tests to pair it with → Treatment options at this number.

8. **cost-breakdown** — price-intent keywords.
   H2s: The total, up front (table) → What drives the price → What insurance and state mandates cover (as of 2026) → Ways to lower the cost without lowering your odds → What the research shows about cost vs. outcome → [content-gap question] → What [brand] charges and what's included (brand pricing only from the brand file).

9. **research-roundup** — "What new research says about X" (the "what's new" slot; only with real volume).
   H2s: What changed this year → Study 1 / Study 2 / Study 3 … as H3s inside 2 themed H2s (each: who was studied, what was found, what it means for you) → Where the evidence is still thin → [content-gap question] → How to use this at your next appointment.

10. **decision-guide** — "Is X right for me?".
    H2s: Who X is designed for (checklist) → Who should consider something else → What the research shows → Pros and cons (two lists) → [content-gap question] → Questions to ask your doctor → If you decide yes: next steps.

11. **condition-guide** — a condition and its fertility impact.
    H2s: What [condition] is → Signs and symptoms → How it affects fertility (mechanism) → How it's diagnosed → What the research shows about treatment → [content-gap question] → Treatment paths to pregnancy.

12. **patient-scenarios** — 3–4 realistic profiles ("43, low AMH, one failed IVF").
    H2s: Why one answer doesn't fit everyone → Scenario A → Scenario B → Scenario C (each: the situation, the options, what the evidence says) → What the research shows across scenarios → [content-gap question] → Finding your own path.

## Title shapes (the title is the H1; primary keyword near the front; 50–70 characters ideal, 90 max)

| id | Shape | Example |
|---|---|---|
| T1 | `[Keyword]: What It Is, Who It's For, and [Actionable Angle]` | Embryo Banking: What It Is, Who It's For, and How Many to Bank |
| T2 | `[Keyword question]? [Direct-answer hook]` | Can You Get Pregnant With Low AMH? Yes, and Here's How |
| T3 | `N [Things] About [Keyword] [Qualifier]` | 7 Causes of Recurrent Implantation Failure Standard Tests Miss |
| T4 | `[Keyword] vs. [Alternative]: Which [Outcome]?` | Mini IVF vs. Conventional IVF: Which Gets More Embryos? |
| T5 | `[Keyword] Explained: [Number/Range] and What It Means for You` | FSH Levels Explained: Ranges by Age and What They Mean for You |
| T6 | `How to [Verb + Keyword]: [Specific Promise]` | How to Prepare for Egg Retrieval: A Week-by-Week Plan |
| T7 | `[Keyword] Cost in 2026: [Breakdown Angle]` | Egg Freezing Cost in 2026: Every Fee, and What Insurance Covers |
| T8 | `Is [Keyword] Right for You? [Decision Tool]` | Is Natural Cycle IVF Right for You? A 6-Question Checklist |
| T9 | `[Keyword] Timeline: [Stage Range]` | IVF Timeline: From First Consult to Pregnancy Test |
| T10 | `Why [Problem] Happens and What Actually Helps` | Why Embryos Fail to Implant and What Actually Helps |
| T11 | `[Keyword]: N Myths, and What the Evidence Says` | Fertility After 40: 7 Myths, and What the Evidence Says |
| T12 | `[Keyword] at [Age/Situation]: [Angle]` | IVF at 44 With Low AMH: Three Paths That Work |

Avoid overused patterns already on the blogs: "What New Research Actually Shows" (RFC has 3), "Step-by-Step Guide" (both), "AI" in Aurea titles (8 already) unless the topic is AI itself.
