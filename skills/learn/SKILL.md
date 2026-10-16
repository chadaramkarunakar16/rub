---
name: learn
description: Step 3a of RUB. From a researched startup, make a week-by-week learn plan - what technology and skills you must learn to build your own version by hand, without AI writing the code - as an HTML page with exercises and resources.
argument-hint: "<study slug or folder> [beginner|some-coding|developer] [hours per week]"
disable-model-invocation: true
---

Make a learn plan for: **$ARGUMENTS**

1. Find the study folder (`studies/<slug>`). It must contain `case.json`; if it does not, tell the user to run
   `/rub:research <startup>` first and stop.
2. Read the level and weekly hours from the arguments. Defaults: `beginner`, 10 hours per week. Say which you used.
3. Delegate to `rub:plan-writer` to write only the learn plan: `studies/<slug>/learn.json`, then render
   `LEARN-PLAN.html` with `python "${CLAUDE_PLUGIN_ROOT}/scripts/rubdoc.py" render learn studies/<slug>/learn.json`
   (`python3` on macOS/Linux).
4. If `build.json` already exists, make the learn plan's topic names match each stage's `learn_first`, and re-run `check build`.
5. Delegate to `rub:verifier` with `learn.json` to open every resource link; replace dead or irrelevant ones, then re-run
   `check learn` and `render learn`.
6. Reply with the path to `LEARN-PLAN.html`, the number of weeks and total hours, the week-1 topics, and the first exercise.
   Offer `/rub:plan <slug>` next if there is no build plan yet. Remind the user that the learn plan is the "by hand" path and
   the build plan is the "with an AI assistant" path.
