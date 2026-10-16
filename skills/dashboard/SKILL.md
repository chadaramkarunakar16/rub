---
name: dashboard
description: Build one HTML page that shows everything you have studied so far - studies with evidence counts, open questions, go-to-market plans, and links to every document.
argument-hint: "[folder, default: the current folder]"
disable-model-invocation: true
---

Build the dashboard for **$ARGUMENTS** (use the current folder if empty).

1. Refresh the indexes: for each study folder that has a `ledger.json`, run
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" render <folder>` (`python3` on macOS/Linux).
2. Run `python "${CLAUDE_PLUGIN_ROOT}/scripts/dashboard.py" <root>`. It writes `<root>/DASHBOARD.html`.
3. Tell the user the path and give a three-line summary: how many studies and plans there are, how many claims
   are verified or disputed, and which study has the most open questions.
4. Suggest the most useful next step (for example, verify the study with unchecked claims, or run `/rub:patterns`
   once there are three or more studies).
