---
name: build
description: Step 4 of RUB. Build your own original version phase by phase with the builder agent - the MVP first, then one feature at a time - one stage per run, from a study's build plan (studies/<slug>/build.json) or an older blueprint (blueprints/<slug>/BLUEPRINT.md).
argument-hint: "<study slug or blueprint slug> [phase.stage, e.g. 1.1 or 2.1; default: the next unfinished stage]"
disable-model-invocation: true
---

Build: **$ARGUMENTS**

1. Look for `studies/<slug>/build.json` first, then `blueprints/<slug>/BLUEPRINT.md`. If neither exists, list what is in
   `studies/` and `blueprints/` and suggest `/rub:plan <slug>` (or `/rub:investigate`). Stop there.
2. For a `build.json`, find where the user is: read `studies/<slug>/app/PROGRESS.md` if it exists (the builder writes it). Pick the
   stage the user named, otherwise the **next unfinished stage**. If there is no `app/` yet, that is stage 1.1.
3. **Phase gate.** If the next stage is the first stage of a feature phase (2.1, 3.1, ...), read the previous phase's
   `exit_criteria` first and ask the user whether they were met with real users. If not, say what is missing and recommend finishing
   or shipping the previous phase first. Do not skip ahead on your own. If the user is not there to answer, stop and explain.
4. Say in 5 lines what this stage will create, which earlier code it extends, and what "done" means (its acceptance checks). Then
   ask the user to confirm. Build only this stage; never start a later stage or a later phase's feature early.
5. After confirmation, delegate to `rub:builder` with the study folder, the phase and stage, and the phase brief
   (`prompts/p<phase>-00-phase-brief.md`). The project goes in `studies/<slug>/app/` unless the user names another folder.
6. Report what runs, the command to start it, which acceptance checks pass, anything not verified, and what comes next (the next
   stage, or, at the end of a phase, the "move on when" checks to do with real users before starting the next feature). Remind the
   user that the code is original: nothing is copied from the company studied.
