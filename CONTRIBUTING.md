# Contributing to RUB

Thanks for helping people research, understand and build. Please read [SAFETY.md](SAFETY.md) first: contributions that
reverse engineer private systems, bypass access controls or collect personal data will not be merged.

## Setup

```
pip install pytest
python -m pytest tests -q        # all tests must pass
python scripts/doctor.py         # checks the plugin structure
claude plugin validate .         # validates the manifests
```

## Ways to contribute

- **Reference guides** in `skills/method/references/`: better learning resources, backend patterns, business frameworks,
  marketing channels (with dated evidence).
- **Agents** in `agents/*.md` (frontmatter: `name`, `description`, `tools`, `model`) and **commands** in
  `skills/<name>/SKILL.md` (frontmatter: `name`, `description`, `argument-hint`). Reference scripts and guides with
  `${CLAUDE_PLUGIN_ROOT}/...`; `doctor.py` fails if a referenced file is missing.
- **Scripts** in `scripts/`: standard library only, one file per job, a `--help` that explains it, and tests in `tests/`.
- **Case study fields and renderers** in `scripts/rubdoc.py`. New facts need a confidence label and a source rule in `problems()`.
- **Sample case studies** with real data: every fact needs a working source URL and an `as_of` date. Fictional samples
  must stay marked `"sample": true`.
- **Translations** of the generated pages and prompts.

## Rules for changes

1. Add or update tests for any script change; keep `python -m pytest tests -q` green.
2. HTML output must stay self-contained (no external requests), escape all text, work on a 390px-wide phone, and support dark mode.
3. Anything that states a fact about a company must carry a source and a confidence label.
4. Keep prompts and plans aimed at **original** products.
5. Do not commit anything from `studies/`; it is user data.

## Pull requests

Describe what you changed and why, show a screenshot if a page changed, and mention the tests you ran.
