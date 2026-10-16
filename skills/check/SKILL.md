---
name: check
description: Check your own build against its blueprint. Lists every requirement in the MVP plan, finds where your code implements it, runs it, and reports what is covered, partial or missing, plus what to learn or build next.
argument-hint: "<feature-slug or study slug> [path to your app]"
disable-model-invocation: true
---

Check the build for: **$ARGUMENTS**

This checks the user's own code against the user's own blueprint.

1. Find the plan: `blueprints/<slug>/BLUEPRINT.md` or `studies/<slug>/STUDY.md`. The code is the path
   given, or `blueprints/<slug>/app/`.
2. Ledger: `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" init <plan-folder>/check --subject "<slug> build check" --kind build`
   (`python3` on macOS/Linux).
3. Extract every requirement from the plan's MVP section (features, data model, API endpoints or events,
   non-functional points such as throttling, idempotency or auth). Add each as a ledger `question`.
4. For each requirement, find where the code implements it (Glob, Grep, Read). Record a `choice` claim
   with the file and line as a `file:` source (for example `file:app/src/cursor.ts#L42`), and mark the
   question answered, partial or unresolved with `ledger.py answer`.
5. Run the app's tests or start command (from its README). Record what ran and what failed.
6. Write `<plan-folder>/CHECK.md`:
   - **Coverage**: requirement | status | where in the code | note
   - **What runs**: commands run and results
   - **Gaps**: missing or partial requirements, each with the concept to learn (link to the blueprint's
     learning path) and the smallest next step
   - **Next version**: what v2 in the plan would add
7. Run `ledger.py render <plan-folder>/check`. Reply with the coverage count and the top 3 gaps.
