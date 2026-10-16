---
name: explain
description: Teaching-only mode. Explain how a feature type works, why it is built that way, and what you would need to learn to build it. No code is written.
argument-hint: "<feature> [like <example product>]"
disable-model-invocation: true
---

Explain this feature as a lesson: **$ARGUMENTS**

Follow the `rub:method` skill's method and teaching style.

Choose a kebab-case slug for the feature. In every delegation, give the agent the slug and its exact
output path. Follow the evidence rules in `${CLAUDE_PLUGIN_ROOT}/skills/method/references/evidence.md`:
first run `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" search . "<feature>"` and reuse an earlier
lesson or blueprint if one exists, then `init blueprints/<slug> --kind feature` and add 4-6 checklist
questions before delegating.

1. Delegate research to the `rub:scout` agent; output `blueprints/<slug>/research.md`.
2. Delegate the explanation to the `rub:architect` agent; input `research.md`, output
   `blueprints/<slug>/architecture.md`.
3. From those two files, write `blueprints/<slug>/LESSON.md`:
   - **The feature in one line**
   - **How it works**: plain walkthrough plus a Mermaid diagram
   - **Why it is built that way**: the problem and the trade-offs table
   - **Key concepts**: each with a one-line definition and an analogy
   - **What to learn to build it**: ordered list with one free resource each (use `references/learning.md`)
   - **Check your understanding**: 3 questions, with answers in a collapsed `<details>` block
   - **Sources**
4. Delegate to `rub:verifier` with the folder, fix any disputed claims in LESSON.md, mark
   the checklist with `ledger.py answer`, then run `ledger.py render` and `ledger.py index .`.
5. In your reply, give a 5-sentence summary of the lesson and offer to run
   `/rub:investigate` to design and build the user's own version.
