---
name: observe
description: Study a product by using it like a real customer in a browser. Walks the journey from landing page to sign-up, onboarding, core features and upgrade prompts, takes screenshots, and explains what the experience reveals about the product, its features and its business. Uses only what a normal user can see.
argument-hint: "<product name or URL> [focus, e.g. 'onboarding', 'pricing', 'the AI editor']"
disable-model-invocation: true
---

Observe this product as a customer: **$ARGUMENTS**

Everything comes from the screen: no developer tools, network inspection or code. The user signs in
themselves; the agent never enters passwords or payment details and never completes a purchase.

## Stage 0: Set up
1. Slug and folders: `studies/<slug>/walkthrough/` with `screens/`.
2. Ledger: `python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" init studies/<slug> --subject "<product>" --kind product`
   (`python3` on macOS/Linux). Reuse an existing study's ledger if there is one; read its business.md first.
3. Check which browser is available (built-in, Chrome, or the headless fallback for public pages only).
   Tell the user which one will be used and what that allows.

## Stage 1: Plan the journey
Write `walkthrough/PLAN.md` with 6-12 steps. Default journey, adjusted to the focus:
1. Landing page (desktop and mobile): headline, who it's for, proof, call to action
2. Pricing page: plans, value metric, free tier or trial, what's gated
3. Sign-up: fields asked, sign-in options, friction **(user signs in here)**
4. Onboarding: questions asked, templates, first-run tour, empty states
5. First "aha": the first moment the product delivers value; how many steps and minutes it took
6-9. Core features in the focus area, using test content
10. Limits and upgrade prompts: where the free plan stops and how the upsell is presented
11. Sharing, collaboration and invite loops (view only; don't invite real people)
12. Help, docs, community, integrations

Add checklist questions to the ledger for each step (`ledger.py question`). Show the plan to the user,
note which steps need them to sign in, and ask them to confirm or adjust.
If the user is not there, run only the public steps (1, 2, 12) and say so.

## Stage 2: Walk it
Delegate to `rub:observer` with the product, the walkthrough folder and the plan. When it
stops for a sign-in, ask the user to sign in in that browser, then resume the observer.

## Stage 3: Verify
Delegate to `rub:verifier` with `studies/<slug>`: it checks each `observed` claim against its
screenshot. Fix disputed claims and mark each checklist question with `ledger.py answer`.

## Stage 4: Insight report
Write `studies/<slug>/walkthrough/WALKTHROUGH.md`, citing claim IDs and linking screenshots:
1. **The product in one line**, as the landing page presents it vs as it feels to use
2. **Journey map**: a table of step, what happened, time, friction (1-5), and screenshot
3. **Time to value**: steps and minutes to the first "aha", and what the product does to get you there fast
4. **Feature by feature**: how each feature behaves from the user's side, and (labelled as `pattern`, not
   observed) the common way such a feature is built, linking to `/rub:explain` for a lesson
5. **What it reveals about the business**: who it's built for, how the free tier and upgrade prompts drive
   revenue (product-led vs sales-led), the value metric, the growth loops built into the product
6. **UX patterns worth learning**: good ideas to borrow, with screenshots
7. **Friction and gaps**: where it confused or blocked you, and what a competitor could do better
   (including an India or niche angle)
8. **Your version**: what you'd keep, change and add if you built your own; suggest
   `/rub:investigate` for the most interesting feature
9. **Coverage**: which planned steps were completed, partial or not reached, and why

Then run `ledger.py render studies/<slug>` and `ledger.py index .`, and reply with the journey map,
the 5 key insights, and the path to `WALKTHROUGH.md` and `GALLERY.md`.
