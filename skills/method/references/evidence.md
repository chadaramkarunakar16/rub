# Evidence ledger rules

Every study, blueprint and scan keeps a `ledger.json` in its folder. The ledger is what makes the
reports trustworthy and reusable: each claim gets an ID, a label and its sources; each question the
study must answer is tracked until it is answered.

## Tool

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/ledger.py" <command> <folder> ...
```
Use `python` on Windows and `python3` on macOS/Linux.

| Command | Use |
| --- | --- |
| `init <folder> --subject "Notion" --kind product` | Start a ledger (feature, product, category, build). Safe to re-run; it reuses an existing ledger |
| `question <folder> "Who pays and why?"` | Add a checklist question; prints `Q1` |
| `claim <folder> "text" --label confirmed --source URL --question Q1 --by scout` | Record a claim; prints `E1` |
| `answer <folder> Q1 --status answered --evidence E1,E2` | Mark coverage: answered, partial or unresolved |
| `verify <folder> E1 --result verified --note "..."` | Verifier only |
| `retract <folder> E6 --reason "..." --replaced-by E8` | Withdraw a disputed or wrong claim (kept in the record, struck out in EVIDENCE.md); question links move to the replacement |
| `check <folder>` | Lists errors and warnings, exits 1 on errors |
| `render <folder>` | Writes `EVIDENCE.md` |
| `index <root>` | Writes `INDEX.md` of every ledger under root |
| `search <root> "term"` | Finds earlier claims to reuse |

## Labels
- **confirmed**: a public source states it. Needs a source.
- **observed**: seen while using the product as a normal user. Needs the screenshot as a `file:` source
  (for example `file:walkthrough/screens/03-onboarding.png`) and, where useful, the page URL.
  An observation is what the screen showed; how it works underneath is a `pattern` or our read.
- **pattern**: the standard industry approach. Source optional.
- **choice**: a design decision for the user's own version.
- **estimate**: a number we worked out. Needs sources for its inputs; say how it was worked out.
- **unknown**: could not be established publicly. Record gaps instead of guessing.

## The workflow every pipeline follows
1. **Reuse first.** Run `search` on the workspace root for the subject. Reuse verified claims; don't redo research.
2. **Checklist.** `init`, then add the study's questions before researching.
3. **Record as you go.** Every fact that will appear in a report goes into the ledger first, with its ID.
   Reports cite claims as `[E4]`.
4. **Answer the checklist.** Mark each question answered, partial or unresolved, with evidence.
5. **Verify independently.** Hand the folder to the `verifier` agent. For each disputed claim, record a
   corrected, narrower claim if the evidence supports one, then `retract` the disputed claim with
   `--replaced-by` the new ID (or no replacement), and update the report's citations. Never edit ledger.json by hand.
6. **Finish.** `check` must show 0 errors. `render` writes EVIDENCE.md. `index` refreshes INDEX.md.
   Never call a study complete while questions are still open; say which are partial or unresolved.
