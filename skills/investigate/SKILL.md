---
name: investigate
description: Full RUB pipeline. Research a feature type, explain how and why it works, pick a stack and learning path, verify the evidence, then (after approval) scaffold your own version.
argument-hint: "<feature> [like <example product>]"
disable-model-invocation: true
---

Run the RUB pipeline for: **$ARGUMENTS**

Follow the `rub:method` skill's method and the evidence rules in
`${CLAUDE_PLUGIN_ROOT}/skills/method/references/evidence.md`. Use a short kebab-case slug (for example
`live-cursors`) and keep every file under `blueprints/<slug>/`. In every delegation, give the agent the slug,
the folder, and its exact input and output paths. The ledger tool is
`python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py"` (`python3` on macOS/Linux).

## Stage 0: Reuse and checklist
1. Run `ledger.py search . "<feature>"`. If an earlier blueprint exists, tell the user and offer to extend it.
2. `ledger.py init blueprints/<slug> --subject "<feature>" --kind feature`.
3. Add the checklist with `ledger.py question`:
   What the user experiences; the request and data flow; the core engineering problem; the 2-3 common
   approaches and their trade-offs; what named products have published about it; our chosen design; the
   stack per layer; the learning path; MVP scope; monthly cost at 100 and 10k users; top risks.

## Stage 1: Research
Delegate to `rub:scout`. Output: `research.md`.

## Stage 2: Explain and design
Delegate to `rub:architect`. Input: `research.md`. Output: `architecture.md`.

## Stage 3: Stack, learning path, plan
Delegate to `rub:stack-advisor`. Input: `architecture.md`. Output: `stack-and-plan.md`.

## Stage 4: Verify
Delegate to `rub:verifier` with the folder. Fix or remove every disputed claim in the three
files, then mark each checklist question answered, partial or unresolved with `ledger.py answer`.
`ledger.py check` must show 0 errors.

## Stage 5: Assemble the Blueprint
Combine the three files into `BLUEPRINT.md` using the skill's report format (In one line, How it works,
Why, The stack, What to learn, Build plan, Costs and risks, Sources). Keep the `[E#]` citations. Add 3
check-your-understanding questions to "How it works". Run `ledger.py render blueprints/<slug>` and
`ledger.py index .`.

## Stage 6: Approval gate
Show the user: the feature in one line, the chosen approach and why, the stack in one line per layer, the
MVP scope, estimated monthly cost, and coverage (questions answered / partial / unresolved). Ask:
"Build the MVP now, change the plan, or stop here?" Do not continue until the user answers.

## Stage 7: Build (only if approved)
Delegate to `rub:builder` with the approved BLUEPRINT.md. Then suggest
`/rub:check <slug>` to compare the build against the blueprint.
