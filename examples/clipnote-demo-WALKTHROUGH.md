> **Example output.** This is a real run of `/rub:observe` against **ClipNote, a made-up demo site** served locally for testing, public steps only (no sign-in). ClipNote is not a real product. The run showed the verifier catching two over-claims (E6, E7).

# ClipNote walkthrough (public steps only)

**Scope:** the user could not sign in, so only the public steps ran (landing, pricing, a view of the sign-up page, help discovery). Steps 3 (submit), 4–11 were not reached. Browser: headless Playwright. Nothing was submitted; no credentials were entered. Claim IDs refer to `ledger.json`; E6 and E7 were disputed and are superseded by E8–E14.

## 1. The product in one line
Landing page: "Turn any video into study notes in 30 seconds" for students and creators; paste a YouTube link, get summaries, flashcards and timestamps (E1). How it feels to use: unknown, because no signed-in feature was reached.

## 2. Journey map
| Step | What happened | Time | Friction (1-5) | Screenshot |
|---|---|---|---|---|
| 1 Landing, desktop | Headline, audience, one CTA, one-line proof, no demo (E1, E2) | not timed | 1 | [01](screens/01-landing-desktop.png) |
| 1 Landing, mobile 390px | Same content, one column (E3) | not timed | 1 | [01b](screens/01b-landing-mobile.png) |
| 2 Pricing | 3 plans, student discount, no buttons or nav back (E4, E5) | not timed | 3 | [02](screens/02-pricing.png) |
| 3 Sign-up (viewed only) | Google button, email/password, use-case dropdown (E8) | not timed | 1 | [03](screens/03-signup-view.png) |
| 12 Help/docs/etc. | Nothing linked; six guessed paths 404 (E9–E14) | not timed | 4 | [help.html](screens/04-helphtml-404.png) |
| 4–11 | Not reached (need sign-in) | – | – | – |

## 3. Time to value
Not measured. The first "aha" is behind sign-up. The only public friction signal is that the CTA says "Start free — no card needed" (E2).

## 4. Feature by feature
Not observed (no signed-in access). Pattern, not observed: a "video to notes" feature is typically a pipeline that fetches the transcript, chunks it, and has an LLM summarise each chunk. See `/rub:explain` for a lesson.

## 5. What it reveals about the business
- **Built for:** students first (student 50% off Pro with .edu/.ac.in, E5), creators second (sign-up dropdown shows "Studying", E8; other options not seen on screen).
- **Model:** product-led freemium. Free is 3 videos a month, summaries only; Pro ₹299/month unlimited plus flashcards and export; Team $12/seat (E4, E5). Value metric is videos per month, then seats.
- **No trial, no annual plan** (E5).
- **Growth loops:** none observed publicly. The Team plan hints at a shared-workspace loop, unverified.

## 6. UX patterns worth learning
- One CTA, repeated, with "no card needed" removing a common objection (E2).
- Mobile parity: the same short page works in one column (E3).

## 7. Friction and gaps
- Landing advertises flashcards, but pricing gates them to Pro (E1, E5): a likely expectation gap at the free limit.
- Pricing page has no sign-up buttons and no way back to the site (E5).
- Pro in rupees, Team in dollars: mixed currency (E5).
- No proof beyond one line; no demo or screenshot (E2).
- No public help, docs, community or integrations found at six guessed paths (E9–E14), and nothing linked (limitation: paths were guessed).
- Screenshots show garbled characters (e.g. "â‚¹" for ₹): a page encoding problem, noted by the verifier, not a ledger claim.
- India/niche angle: rupee pricing and .ac.in discount are a head start; a competitor could add Indian-language videos, UPI and exam-prep formats. This is an idea, not an observation.

## 8. Your version
Keep: single CTA, "no card needed", student discount. Change: show a live demo and put flashcards in the free tier at a small cap; one currency; a pricing page with CTAs. Add: help page, a public sample note. Next step: `/rub:investigate` on the video-to-notes feature, once someone can sign in.

## 9. Coverage
- Completed: 1, 2, 12 (12 found nothing).
- Partial: 3 (viewed, not submitted).
- Not reached: 4–11 (sign-in needed).

Verification: E1–E5 and E8–E14 verified; E6 and E7 disputed and superseded. E9–E14 screenshots carry a URL banner added by the capture script (annotation, not site content).
