#!/usr/bin/env python3
"""RUB snapshots: keep dated copies of public pages (pricing, changelog, homepage)
as plain text and show what changed between the two latest copies.

Layout: <study>/snapshots/<page-name>/<YYYY-MM-DD>.md

Commands
  path  <study> <page-name>        print today's snapshot path (creates the folder)
  diff  <study> <page-name>        unified diff of the two latest snapshots
  list  <study>                    pages and their snapshot dates

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import sys
from pathlib import Path


def page_dir(study: str, page: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in page.lower()).strip("-")
    if not safe:
        sys.exit("error: page name must contain letters or digits")
    return Path(study) / "snapshots" / safe


def cmd_path(a) -> None:
    d = page_dir(a.study, a.page)
    d.mkdir(parents=True, exist_ok=True)
    print(d / f"{dt.date.today().isoformat()}.md")


def cmd_diff(a) -> int:
    d = page_dir(a.study, a.page)
    snaps = sorted(d.glob("*.md"))
    if len(snaps) < 2:
        print(f"only {len(snaps)} snapshot(s) in {d}; need two to compare")
        return 0
    old, new = snaps[-2], snaps[-1]
    a_lines = old.read_text(encoding="utf-8").splitlines()
    b_lines = new.read_text(encoding="utf-8").splitlines()
    diff = list(difflib.unified_diff(a_lines, b_lines, fromfile=old.name, tofile=new.name, lineterm="", n=1))
    if not diff:
        print(f"no changes between {old.name} and {new.name}")
        return 0
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    print(f"{old.stem} -> {new.stem}: +{added} / -{removed} lines")
    print("\n".join(diff))
    return 0


def cmd_list(a) -> int:
    root = Path(a.study) / "snapshots"
    if not root.is_dir():
        print("no snapshots yet")
        return 0
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        dates = [s.stem for s in sorted(d.glob("*.md"))]
        print(f"{d.name}: {', '.join(dates) if dates else '(empty)'}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="RUB page snapshots")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("path", cmd_path), ("diff", cmd_diff)):
        s = sub.add_parser(name); s.add_argument("study"); s.add_argument("page"); s.set_defaults(fn=fn)
    s = sub.add_parser("list"); s.add_argument("study"); s.set_defaults(fn=cmd_list)
    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
