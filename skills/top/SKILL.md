---
name: top
description: Find the leading paid software in a category right now and compare why each one is winning (customers, pricing, moat, growth, key features), then recommend which to study first.
argument-hint: "<category, e.g. AI video editing, CRM for small business, AI coding tools>"
disable-model-invocation: true
---

Map the top paid software in this category: **$ARGUMENTS**

Follow the evidence rules in `${CLAUDE_PLUGIN_ROOT}/skills/method/references/evidence.md`. Keep a
category ledger with `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" init studies/_categories/<category-slug> --kind category`
and record the ranking evidence there; each product's strategist uses its own product ledger.

1. Search for current market evidence: recent rankings and reviews (G2, Capterra, Product Hunt), funding
   and revenue news, and credible analyst or press coverage. Use the current year in queries.
   Pick the 5-8 leading paid products, and say what "top" is based on (revenue, users, growth, ratings).
2. For the top 3-5, delegate to `rub:strategist` agents in parallel (one per product),
   writing into `studies/<product-slug>/business.md`.
3. Write `studies/_categories/<category-slug>.md`:
   - **The category in one line**, and why it is growing now
   - **Comparison table**: product | who pays | pricing model and entry price | moat | growth engine | standout feature
   - **Patterns**: what the winners have in common, and where they differ
   - **Gaps**: underserved customers or niches (including India-specific ones) a small team could own
   - **Study next**: which product to run `/rub:research` on first, and why
   - **Sources**
4. Delegate to `rub:verifier` for the category ledger, fix disputed claims, then run
   `ledger.py render` and `ledger.py index .`.
5. In your reply, give the comparison table and the "Study next" recommendation.
