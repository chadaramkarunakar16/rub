---
name: method
description: Teach how a type of product feature works (the user-facing behaviour, the backend pattern behind it, why it is designed that way) and turn that into a plan and working scaffold for the user's own version. Use when the user says "how does X work", "how would I build X", "explain the backend of a feature like X", "what do I need to learn to build X", or names a feature they want to recreate in their own project.
---

# RUB

RUB turns "I saw a feature I like" into "I understand it and I have my own working version."
It works on **feature types** (realtime cursors, infinite feed, full-text search, AI chat with memory,
collaborative docs, payments with retries, short-video upload and playback) and explains them from
general engineering knowledge and public sources. The user's own version is designed and written fresh.

## The four questions

Every blueprint answers these, in this order:

1. **What is it?** The feature as a user experiences it: what they do, what they see, what must feel instant.
2. **How does it work?** The standard architecture for this kind of feature: client, API, data store,
   background jobs, realtime channel, third-party services. Show the request/data flow step by step.
3. **Why is it built that way?** The core engineering problem (latency, consistency, scale, cost, abuse)
   and the trade-offs between the 2-3 common approaches.
4. **How do we build our own?** Components to build, tools to use, what to learn first, an MVP path,
   costs, risks, and a scaffold the user can run.

## Where knowledge comes from

Use general engineering knowledge first, then confirm and enrich it from public material:
official engineering blogs, product documentation and API references, conference talks,
well-known open-source projects that implement the same pattern, and textbooks or courses.
Cite every specific claim about a named company ("Figma uses CRDT-like multiplayer") with its source URL.
When nothing public confirms a detail about a named product, say so and describe the common pattern instead.
Label each claim: **Confirmed** (a public source says it), **Common pattern** (standard industry approach),
or **Our choice** (a design decision for the user's version).

## Output format: the Blueprint report

Write `blueprints/<feature-slug>/BLUEPRINT.md` with these sections:

1. **In one line**: the feature in plain words.
2. **How it works**: a short walkthrough plus a Mermaid sequence or flow diagram.
3. **Why it is built this way**: the problem, the approaches, the trade-offs (a small table).
4. **The stack**: for each layer (frontend, API, database, realtime, storage, jobs, AI, hosting),
   the recommended tool, one alternative, and why. Prefer free tiers and tools that work well in India
   (Razorpay for payments, Indian-region hosting where latency matters).
5. **What to learn**: an ordered learning path, each step with what to learn, why it is needed for this
   feature, and one good free resource.
6. **Build plan**: MVP (smallest version that proves the idea), then v2 and v3 upgrades.
7. **Costs and risks**: rough monthly cost at 100 / 10k users, and the top risks with mitigations.
8. **Sources**: every link used.

Then, only after the user approves the plan, scaffold the MVP in `blueprints/<feature-slug>/app/`.

## Teaching style

- Explain like a senior engineer mentoring a capable beginner: plain words first, then the proper term.
- Use one concrete analogy per hard concept.
- End the explanation with 3 quick check-your-understanding questions.
- Keep "how it works" honest: describe the general pattern, not guessed internals of a specific company.

## References

- Backend patterns by feature type: [references/patterns.md](references/patterns.md)
- Learning resources by topic: [references/learning.md](references/learning.md)
- Business frameworks for product studies: [references/business.md](references/business.md)
- Evidence ledger rules and tool: [references/evidence.md](references/evidence.md). Every pipeline uses it.
- Startup and funding research: [references/startups.md](references/startups.md)

## Product studies

When the user wants to understand a whole paid product (why it is winning as a business as well as how
its features work), use the `strategist` agent for the business teardown and run the four questions on
the product's top value features. The `/rub:research` and `/rub:top` workflows
do this end to end.

## Market research

To understand which startups get funded and why, use `market-scout` to build a dataset
(`/rub:scan`, `/rub:startup`) and `opportunity-mapper` to connect the dots
(`/rub:patterns`). `/rub:compare` and `/rub:track` cover
side-by-side comparison and changes over time. `/rub:observe` studies a product by using it
like a customer in a browser (the `observer` agent), recording only what the screen shows. `/rub:check` compares the user's own build
with its blueprint, and `/rub:content` turns findings into teaching content.
