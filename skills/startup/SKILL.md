---
name: startup
description: Quick profile of one startup (about 15 minutes) covering problem, customer, business model, funding story, why investors backed it, how it is scaling, and the lesson for you. Lighter than a full study; adds the company to your dataset.
argument-hint: "<startup name or website>"
disable-model-invocation: true
---

Profile this startup: **$ARGUMENTS**

1. Check for earlier work: `python "${CLAUDE_PLUGIN_ROOT}/scripts/dataset.py" query studies/_all --where name=<name>`
   (skip if `studies/_all` does not exist yet) and look for `studies/<slug>/`. Reuse what exists.
2. Delegate to `rub:market-scout` with scan folder `studies/_scans/profiles/` and this one company.
   It writes `studies/_scans/profiles/companies/<slug>.json`.
3. Delegate to `rub:strategist` for a focused teardown of sections 1-3, 8, 9 and 11
   (one line, who pays, pricing, funding story, scaling, founder lessons), writing
   `studies/<slug>/business.md` with ledger claims.
4. Delegate to `rub:verifier` with `studies/<slug>`. Fix any disputed claim.
5. Run `dataset.py merge studies/_scans/profiles` and `dataset.py combine studies`.
6. Reply with a one-screen profile:
   - **What it does**, for whom, and the problem it removes
   - **Business model** and entry price
   - **Funding**: rounds, amounts, investors, and the public reason they invested
   - **How it is scaling** (signals with dates)
   - **The lesson**: what you could learn or build from it, including an India or niche angle
   Then offer `/rub:research <name>` for the full HTML case study.
