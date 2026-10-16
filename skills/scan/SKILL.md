---
name: scan
description: Build a dataset of startups from public sources (a YC batch, recently funded AI startups, a category) with problem, customer, business model, funding, investors and traction for each, plus a summary of where the money is going.
argument-hint: "<what to scan, e.g. 'YC S26 AI companies', 'AI startups funded in last 90 days', 'Indian AI SaaS seed rounds 2026'> [max N]"
disable-model-invocation: true
---

Scan: **$ARGUMENTS**

Tools (use `python3` on macOS/Linux):
- `python "${CLAUDE_PLUGIN_ROOT}/scripts/dataset.py"` for records, CSV and summaries
- Source guide: `${CLAUDE_PLUGIN_ROOT}/skills/method/references/startups.md`

## Stage 1: Define the scan
Pick a kebab-case scan slug with the date (for example `yc-s26-ai-2026-10`). Folder:
`studies/_scans/<scan-slug>/`. Write `<scan>/SCOPE.md` with: what is included, the time window, the sources
to use, and the maximum number of companies (default 30; ask before going above 60).

## Stage 2: Build the list
Find the companies from the sources in the guide. Write `<scan>/list.md` (name, website, why included,
source URL). Remove duplicates. If the list is longer than the maximum, say how you chose.

## Stage 3: Profile in parallel
Split the list into slices of about 8 companies and run one `rub:market-scout` agent per
slice in parallel, each writing `<scan>/companies/<slug>.json`. Give each worker the scan folder and its
exact names.

## Stage 4: Validate and merge
Run `dataset.py validate <scan>` and send any broken records back to a market-scout to fix. Then run
`dataset.py merge <scan>` (writes `companies.csv` and `SUMMARY.md`) and `dataset.py combine studies`
(updates the all-companies dataset).

## Stage 5: Spot-check
Delegate to `rub:verifier` with 5 randomly chosen records: check each record's funding,
investors and pricing against its sources. If more than one is disputed, re-check the whole scan's
funding fields before reporting.

## Stage 6: Report
In your reply give: the number of companies, the breakdown by category and business model, the largest
rounds, the most active investors, 3-5 patterns you noticed, and suggest next steps:
`/rub:patterns` to connect the dots, or `/rub:research <company>` on the most
interesting ones.
