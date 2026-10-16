---
name: opensource
description: Learn from a public open-source repository (or your own). Maps the licence, stack, folder layout, data model and one feature end to end, then gives a reading order, a learn list and a smaller version to build yourself.
argument-hint: "<GitHub URL or local folder> [feature to trace]"
disable-model-invocation: true
---

Study this open-source project: **$ARGUMENTS**

Folder: `studies/<repo-slug>/`. Ledger: `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" init studies/<repo-slug> --subject "<repo>" --kind repo`
(`python3` on macOS/Linux).

## Stage 0: Get the code
- A GitHub URL: `git clone --depth 1 <url> studies/<repo-slug>/repo`. If cloning is blocked, ask the user to
  download the repo and give the folder path.
- A local folder: use it where it is and never modify it.
- Check the licence first (`repomap.py` does this). If there's no licence or it is copyleft/restrictive, tell the user what
  that means for reuse before going further. Studying is still fine.

Add checklist questions: what is it for; stack; folder layout; data model; the main feature end to end; design
choices; quality signals; reading order; learn list; the user's own smaller version.

## Stage 1: Tour
Delegate to `rub:cartographer` with the repo folder, the study folder, and the feature to trace (if any).
It writes `repomap.md` and `TOUR.md`.

## Stage 2: Verify
Delegate to `rub:verifier`. It opens the cited files and checks each `confirmed` claim; disputed
claims are fixed or retracted. Then run `ledger.py render` and `ledger.py index .`.

## Stage 3: Your version
If the user wants to build their own, hand over to `/rub:build` with `TOUR.md` as the study. The build starts
from the smaller version in the tour and is written fresh, with the licence reminder.

## Stage 4: Reply
Give: what the project is, the stack, the key design choice, the first 5 files to read, the licence in plain words,
and the path to `TOUR.md`. Offer to trace a second feature or to compare this repo with a similar one.
