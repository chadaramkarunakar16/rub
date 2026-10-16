---
name: launch
description: Build a go-to-market plan for your product. Reconstructs how a competitor won its users (public evidence), checks which marketing channels are working right now for your audience, and produces a phased plan to an MRR target with the user math, a weekly schedule and a tickable visual roadmap.
argument-hint: "<your product> like <competitor> [price e.g. $9/mo or ₹299/mo] [target e.g. $10k MRR] [audience/region]"
disable-model-invocation: true
---

Make a go-to-market plan for: **$ARGUMENTS**

Folder: `studies/<product-slug>/gtm/`. Ledger: `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" init studies/<product-slug>/gtm --subject "<product> go-to-market" --kind plan`
(`python3` on macOS/Linux). Follow the evidence rules and the ethics rules in
`${CLAUDE_PLUGIN_ROOT}/skills/method/references/channels.md`.

## Stage 0: Inputs
From the arguments, or by asking the user (one short question, defaults in brackets):
your product and its one-liner; the competitor to learn from; price [about 60% of the competitor's entry plan];
target MRR [$10k or ₹5L]; audience and region [what the product suggests]; hours per week the user can spend
on marketing [10]. Reuse `studies/<competitor-slug>/business.md` and any walkthrough if they exist
(`ledger.py search . "<competitor>"`). Add checklist questions to the ledger: competitor's first-100-users
tactics; their channels today; pricing; which channels are working now for this audience; our positioning;
our price; the funnel assumptions; the phase plan; the first 4 weeks; the risks.

## Stage 1: Optional look at the competitor
If there's no business study yet, offer to run `/rub:startup <competitor>` first, and
`/rub:observe <competitor> pricing and onboarding` to see their funnel as a customer.

## Stage 2: Research and plan
Delegate to `rub:growth-strategist` with the inputs, the folder, and the user's weekly hours.
It writes `playbook.md`, `channels-now.md`, `plan.json`, `ROADMAP.html` and `MATH.md`.

## Stage 3: Verify
Delegate to `rub:verifier` with the folder. Fix or retract disputed claims and update
`plan.json` if a task relied on one; re-run `python "${CLAUDE_PLUGIN_ROOT}/scripts/gtm.py" render <folder>/plan.json`.
Check every task against the ethics rules; rewrite any that break them.

## Stage 4: The plan document
Write `<folder>/GTM.md`:
1. **Positioning**: one line, the first audience, the pain, the promise, and the difference from the competitor
2. **Price and plans**, compared with the competitor's
3. **How the competitor won** (short, cited) and **what's working now** (short, cited, dated)
4. **The numbers**: from MATH.md, plus a plain reality check (is the timeline realistic for the hours available?)
5. **The plan**: the three phases with their tasks, each showing where it was learned from
6. **First 4 weeks**: a day-by-day or week-by-week schedule within the user's hours
7. **Experiments**: 3-5 channel experiments, each with a metric, a success threshold and a stop rule
8. **Content engine**: the recurring content (for example one short video a day) and how
   `/rub:content` can produce it from the user's studies
9. **Risks**, and what to do if the first phase misses its target
10. **Sources**

Run `ledger.py render <folder>` and `ledger.py index .`.

## Stage 5: Reply
Give the positioning line, price, phase targets with paying-user counts, the 5 highest-leverage tasks, and the
paths to `GTM.md` and `ROADMAP.html` (open it in a browser; ticks are saved there). Offer to turn the first week's
content into scripts with `/rub:content`, and to re-check the plan monthly against real numbers.
