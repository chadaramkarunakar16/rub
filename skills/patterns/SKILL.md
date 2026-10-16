---
name: patterns
description: Connect the dots across every startup and product you have researched. Shows where money is going, recurring problems, why companies got funded, crowded vs open spaces, and ranked opportunity ideas you could build.
argument-hint: "[focus, e.g. 'India', 'creators', 'AI agents for SMBs', 'healthcare']"
disable-model-invocation: true
---

Find patterns and opportunities. Focus: **$ARGUMENTS** (if empty, look across everything).

1. Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/dataset.py" combine studies` (`python3` on macOS/Linux).
   If there are fewer than 15 companies in `studies/_all/companies.csv`, tell the user the sample is small and
   suggest a `/rub:scan` first; continue only if they agree or are not there to answer.
2. Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" index .` so every study is listed in INDEX.md.
3. Delegate to `rub:opportunity-mapper` with the focus. It writes
   `studies/_patterns/<focus-slug>-<date>.md`.
4. Reply with: the sample size, the top 3 money trends, the top 3 recurring problems, and the ranked
   opportunity table (idea | who pays | why now | learns from | score). Offer to run
   `/rub:research` on the companies it recommends, or `/rub:investigate` on the
   top opportunity's core feature.
