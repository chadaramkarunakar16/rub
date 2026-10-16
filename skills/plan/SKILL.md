---
name: plan
description: Step 3b of RUB. From a researched startup, make a phase-by-phase build plan - an MVP first, then one feature per phase - with stack, architecture, data model, API, and stage-by-stage prompts you paste into Claude Code or Cursor to vibe-code your own original version. HTML page plus prompt files.
argument-hint: "<study slug or folder> [stack preference, e.g. 'Next.js + Supabase'] [first feature to build]"
disable-model-invocation: true
---

Make a build plan for: **$ARGUMENTS**

1. Find the study folder (`studies/<slug>`). It must contain `case.json`; if it does not, tell the user to run
   `/rub:research <startup>` first and stop. Read `case.json` (especially features, USP, competitors and white space), the feature
   teardowns under `features/`, and the walkthrough if present.
2. Delegate to `rub:plan-writer` to write only the build plan: `studies/<slug>/build.json`. Pass along the stack preference and the
   first feature, if the user gave them. The plan is **phased**: Phase 1 is the MVP, and each later phase adds exactly one feature
   with a reason, stages, prompts and measurable exit criteria. It runs `check build`, renders `BUILD-PLAN.html`, and exports the
   prompts into `studies/<slug>/prompts/` (`00-project-context.md`, then per phase a brief and one file per stage, plus `PROMPTS.md`).
3. Delegate to `rub:verifier` with `build.json` to check the stack choices and the stage order. Apply its fixes and re-run
   `python "${CLAUDE_PLUGIN_ROOT}/scripts/rubdoc.py" check build studies/<slug>/build.json`, `render build ...` and `export ... --out studies/<slug>/prompts`.
4. Reply with the path to `BUILD-PLAN.html`, the stack in one line, the roadmap (Phase 1 MVP with its hours, then each feature phase with
   the one feature and why it is next), and the first prompts to paste (context prompt, Phase 1 brief, stage 1.1). Explain the rhythm:
   build the MVP, ship it to a few real users, tick the "move on when" checks, then add the next feature as its own phase. The plan
   builds an original product, not a copy.
5. Offer: `/rub:learn <slug>` for the by-hand learn plan, `/rub:build <slug>` to have the builder agent write the next stage now, and
   `/rub:launch` for a marketing plan.
