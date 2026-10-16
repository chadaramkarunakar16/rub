---
name: compare
description: Compare two to five products or startups side by side on customer, pricing, model, moat, growth, funding, scaling and key features, and explain why each is winning in its own way.
argument-hint: "<product A> vs <product B> [vs ...]"
disable-model-invocation: true
---

Compare: **$ARGUMENTS**

1. For each product, reuse `studies/<slug>/business.md` if it exists and is under 60 days old
   (check its ledger `updated` date). Otherwise delegate to `rub:strategist` (in parallel
   for several products) to write it.
2. Write `studies/_compare/<a>-vs-<b>.md`:
   - **One line each**
   - **Side-by-side table**: who pays | job to be done | pricing model and entry price | value metric |
     moat | growth engine | funding to date | latest round | scaling signals | standout feature
   - **Where they really differ**: positioning, customer, technology bets
   - **Why each is winning**: each one's advantage in plain words
   - **What a newcomer could do differently**: an underserved customer, a price point, a region (including
     India), or a feature gap
   - **Sources**: link to each business.md and its EVIDENCE.md
3. Delegate to `rub:verifier` for any product whose ledger has unverified `confirmed` claims.
4. Reply with the table and the "what a newcomer could do differently" section.
