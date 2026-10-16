---
name: research
description: Step 1 and 2 of RUB. Give it a startup or software product and get an HTML case study from public sources - when it started, founders, funding and valuation, market position, features, USP, business model, how it grows, its technology, why it leads, and its drawbacks.
argument-hint: "<startup or product name or website>"
disable-model-invocation: true
---

Research this startup or product: **$ARGUMENTS**

Use a kebab-case slug. Everything goes under `studies/<slug>/`. Follow the `rub:method` skill and the evidence
rules in `${CLAUDE_PLUGIN_ROOT}/skills/method/references/evidence.md`. The ledger tool is
`python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py"` (`python3` on macOS/Linux). In every delegation give the agent the
slug, the folder and the exact output path. Do not stop to ask the user questions; make sensible choices and say
what you chose.

Begin your reply with one sentence telling the user what you are about to do.

## Stage 0: Reuse and checklist
1. `ledger.py search . "<name>"`. If the product was researched before, read what exists and update it rather than redo it.
   If it appears in a scan under `studies/_scans/`, read that record first.
2. `ledger.py init studies/<slug> --subject "<name>" --kind product`.
3. Add the checklist with `ledger.py question`: when it was founded and by whom; what it builds and for whom; the
   features customers pay for; the unique selling point; pricing and the value metric; the business model; funding rounds,
   investors, total raised and valuation; why it was funded; market position; which competitors are doing well and how each differentiates; the white space; how it got and grows
   customers; the technology (what is public); drawbacks and risks; opportunities for a smaller newcomer.

## Stage 1: Business and funding
Delegate to `rub:strategist`. Output `studies/<slug>/business.md` and the top value features.

## Stage 1b: Competitors
Delegate to `rub:competitor-analyst` (it can run in parallel with Stage 3). Output `studies/<slug>/competitors.md`: the
3-5 competitors that are doing well now, how each differentiates (price, niche, speed, integrations, region,
distribution, brand), what each is strong and weak at, and the white space nobody serves well.

## Stage 2: Use it as a customer (if possible)
If the product has a public website or free trial, run the observe workflow on its landing page, pricing and onboarding
(public pages only) into `studies/<slug>/walkthrough/`. If browsing is not possible in this session, skip it and say so.

## Stage 3: How it works
Pick the top 3 value features. For each, run `rub:scout`, then `rub:architect`, then `rub:stack-advisor`, writing
`research.md`, `architecture.md` and `stack-and-plan.md` into `studies/<slug>/features/<feature-slug>/`. Independent
features can run in parallel. Also ask the scout to look for public technology evidence for the product itself: engineering
blog posts, job posts that name the stack, docs, public repos, status page, conference talks. These and only these may be
marked `confirmed` in the tech section.

## Stage 4: Verify
Delegate to `rub:verifier` with the folder. Fix or retract disputed claims; answer each checklist question with
`ledger.py answer`; `ledger.py check` must show 0 errors.

## Stage 5: Write the case study
Delegate to `rub:case-writer` with the folder. It writes `case.json` and renders `CASESTUDY.html`.
Then delegate to `rub:verifier` once more with `case.json`; fix every problem it reports in `case.json`, re-run
`python "${CLAUDE_PLUGIN_ROOT}/scripts/rubdoc.py" check case studies/<slug>/case.json` and
`render case studies/<slug>/case.json`.
Run `ledger.py render studies/<slug>` and `ledger.py index .`.

## Stage 6: Reply
Give the path to `CASESTUDY.html` and, in about 8 lines: what it is, who it is for, founders and when it started, funding and
valuation (say "not publicly confirmed" when it is), the USP, why it leads, how its main competitors differentiate and the
biggest gap nobody serves, the biggest drawback, and any facts that stayed unknown. Then offer the next steps:
- `/rub:learn <slug>` for a learn plan (what to study to build it yourself)
- `/rub:plan <slug>` for a build plan with step-by-step prompts for vibe coding
- `/rub:launch` for a marketing plan once a product idea is chosen
