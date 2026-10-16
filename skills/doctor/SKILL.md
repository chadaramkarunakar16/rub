---
name: doctor
description: Check that RUB is installed correctly and your machine is ready (plugin files, Python, git, browser fallback, internet). Run this first if something doesn't work.
disable-model-invocation: true
---

Run the health check and explain the result in plain words:

`python "${CLAUDE_PLUGIN_ROOT}/scripts/doctor.py"` (`python3` on macOS/Linux)

For every `FAIL` line, say what it means and the exact fix. For every `warn`, say what feature is affected
(for example, no Playwright means `/rub:observe` needs the built-in browser or Chrome instead)
and give the one-line install command. Do not change any files yourself. End with one sentence saying whether
the user is ready to start and which command to try first.
