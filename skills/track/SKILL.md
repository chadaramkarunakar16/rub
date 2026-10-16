---
name: track
description: Track how a product changes over time from its public pages (pricing, changelog, homepage positioning, careers). Saves a dated text snapshot each run and explains what changed and what it signals about the business.
argument-hint: "<product name> [pages: pricing, changelog, homepage, careers]"
disable-model-invocation: true
---

Track public changes for: **$ARGUMENTS**

Tool: `python "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py"` (`python3` on macOS/Linux).
Study folder: `studies/<product-slug>/` (create it if needed).

1. Pages: use the ones named, or default to pricing, changelog (or "what's new"/release notes), homepage and
   careers. Find each page's URL on the product's site.
2. For each page:
   - Fetch it with WebFetch and ask for the page's meaningful text as Markdown: plan names, prices, limits,
     feature lists, headlines, release-note entries with dates, open roles by team. No navigation or footer.
   - Get today's path with `snapshot.py path studies/<slug> <page>` and write the text there, with the URL
     and fetch date at the top.
   - Run `snapshot.py diff studies/<slug> <page>`.
3. Write `studies/<slug>/CHANGES.md` (newest entry on top): date, and for each page with changes, what
   changed in plain words and what it likely signals (price increase → pushing upmarket; new AI feature
   → following a trend; hiring sales roles → moving to sales-led; new region → expansion). Label signals as
   our read.
4. If this is the first snapshot, say so and suggest re-running monthly. Offer to set it up as a scheduled
   task if the user wants automatic tracking.
