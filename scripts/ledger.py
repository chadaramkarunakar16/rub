#!/usr/bin/env python3
"""RUB evidence ledger.

Every study or blueprint folder keeps a ledger.json that records:
  - questions the study must answer (Q1, Q2, ...) and their coverage status
  - claims (E1, E2, ...) with a label, sources, the question they answer, and verification state

Commands
  init      <dir> --subject TEXT --kind feature|product|category|build|plan|repo
  question  <dir> TEXT
  claim     <dir> TEXT --label LABEL [--source URL ...] [--question Q1 ...] [--by AGENT]
  answer    <dir> QID --status answered|partial|unresolved [--evidence E1,E2] [--note TEXT]
  verify    <dir> EID --result verified|disputed|unverifiable [--note TEXT]
  retract   <dir> EID --reason TEXT [--replaced-by E8,E9]
  check     <dir> [--strict]
  render    <dir>
  index     <root>
  search    <root> TERM

Labels
  confirmed  a public source states it            (needs >= 1 source)
  observed   seen while using the product         (needs a screenshot file: source or the page URL)
  pattern    standard industry approach           (source optional)
  choice     our design decision                  (no source needed)
  estimate   a number we estimated                (needs >= 1 source for its inputs)
  unknown    could not be established publicly    (records the gap)

Standard library only. Works on Windows, macOS and Linux.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import json
import os
import sys
import tempfile
import time
from pathlib import Path

LEDGER = "ledger.json"
LABELS = ("confirmed", "observed", "pattern", "choice", "estimate", "unknown")
NEEDS_SOURCE = ("confirmed", "observed", "estimate")
Q_STATUS = ("open", "answered", "partial", "unresolved")
V_RESULTS = ("verified", "disputed", "unverifiable")
KINDS = ("feature", "product", "category", "build", "plan", "repo")


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def fail(msg: str, code: int = 2) -> "None":
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------- storage ----------

@contextlib.contextmanager
def locked(folder: Path, timeout: float = 15.0):
    """Simple cross-platform lock so parallel agents don't overwrite each other."""
    lock = folder / (LEDGER + ".lock")
    start = time.monotonic()
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            break
        except FileExistsError:
            # Treat a lock older than 2 minutes as stale (its writer died).
            try:
                if time.time() - lock.stat().st_mtime > 120:
                    lock.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.monotonic() - start > timeout:
                fail(f"ledger is locked by another writer: {lock}")
            time.sleep(0.1)
    try:
        yield
    finally:
        lock.unlink(missing_ok=True)


def load(folder: Path) -> dict:
    path = folder / LEDGER
    if not path.exists():
        fail(f"no {LEDGER} in {folder}. Run: ledger.py init {folder} --subject ... --kind ...")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def save(folder: Path, data: dict) -> None:
    data["updated"] = now()
    fd, tmp = tempfile.mkstemp(dir=folder, prefix=".ledger-", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, folder / LEDGER)


def next_id(items: list, prefix: str) -> str:
    nums = [int(i["id"][1:]) for i in items if i["id"][1:].isdigit()]
    return f"{prefix}{(max(nums) if nums else 0) + 1}"


def find(items: list, item_id: str, what: str) -> dict:
    for i in items:
        if i["id"].upper() == item_id.upper():
            return i
    fail(f"{what} {item_id} not found")


def split_ids(values: list[str] | None) -> list[str]:
    out: list[str] = []
    for v in values or []:
        out += [x.strip().upper() for x in v.split(",") if x.strip()]
    return out


# ---------- commands ----------

def cmd_init(a) -> None:
    folder = Path(a.dir)
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / LEDGER).exists() and not a.force:
        print(f"{folder / LEDGER} already exists (use --force to reset). Reusing it.")
        return
    data = {
        "subject": a.subject,
        "kind": a.kind,
        "created": now(),
        "updated": now(),
        "questions": [],
        "claims": [],
    }
    save(folder, data)
    print(f"initialised {folder / LEDGER}")


def cmd_question(a) -> None:
    folder = Path(a.dir)
    with locked(folder):
        data = load(folder)
        qid = next_id(data["questions"], "Q")
        data["questions"].append(
            {"id": qid, "text": a.text, "status": "open", "evidence": [], "note": "", "added": now()}
        )
        save(folder, data)
    print(qid)


def cmd_claim(a) -> None:
    folder = Path(a.dir)
    sources = a.source or []
    if a.label in NEEDS_SOURCE and not sources:
        fail(f"a '{a.label}' claim needs at least one --source")
    for s in sources:
        if not (s.startswith("http://") or s.startswith("https://") or s.startswith("file:")):
            fail(f"source must be a URL (http/https) or file: path, got: {s}")
    with locked(folder):
        data = load(folder)
        qids = split_ids(a.question)
        for q in qids:
            find(data["questions"], q, "question")
        eid = next_id(data["claims"], "E")
        data["claims"].append(
            {
                "id": eid,
                "text": a.text,
                "label": a.label,
                "sources": sources,
                "questions": qids,
                "by": a.by or "",
                "added": now(),
                "verification": None,
                "verification_note": "",
            }
        )
        save(folder, data)
    print(eid)


def cmd_answer(a) -> None:
    folder = Path(a.dir)
    with locked(folder):
        data = load(folder)
        q = find(data["questions"], a.qid, "question")
        ev = split_ids(a.evidence)
        for e in ev:
            find(data["claims"], e, "claim")
        if a.status == "answered" and not ev and not q["evidence"]:
            fail("an 'answered' question needs --evidence (claim IDs)")
        q["status"] = a.status
        q["evidence"] = sorted(set(q["evidence"]) | set(ev), key=lambda x: int(x[1:]))
        if a.note:
            q["note"] = a.note
        save(folder, data)
    print(f"{q['id']} -> {a.status}")


def cmd_verify(a) -> None:
    folder = Path(a.dir)
    with locked(folder):
        data = load(folder)
        c = find(data["claims"], a.eid, "claim")
        c["verification"] = a.result
        c["verification_note"] = a.note or ""
        c["verified_at"] = now()
        save(folder, data)
    print(f"{c['id']} -> {a.result}")


def cmd_retract(a) -> None:
    folder = Path(a.dir)
    with locked(folder):
        data = load(folder)
        c = find(data["claims"], a.eid, "claim")
        repl = split_ids(a.replaced_by)
        for r in repl:
            if r == c["id"]:
                fail("a claim cannot replace itself")
            find(data["claims"], r, "claim")
        c["retracted"] = True
        c["retracted_reason"] = a.reason
        c["replaced_by"] = repl
        c["retracted_at"] = now()
        # move question links over to the replacements
        for q in data["questions"]:
            if c["id"] in q["evidence"]:
                q["evidence"] = sorted((set(q["evidence"]) - {c["id"]}) | set(repl), key=lambda x: int(x[1:]))
        save(folder, data)
    print(f"{c['id']} retracted" + (f", replaced by {', '.join(repl)}" if repl else ""))


def live(claims: list) -> list:
    return [c for c in claims if not c.get("retracted")]


def problems(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    claim_ids = {c["id"] for c in live(data["claims"])}
    for c in live(data["claims"]):
        if c["label"] in NEEDS_SOURCE and not c["sources"]:
            errors.append(f"{c['id']} is '{c['label']}' but has no source")
        if c["verification"] == "disputed":
            errors.append(f"{c['id']} was disputed by the verifier: {c['verification_note']}")
        if c["label"] in ("confirmed", "observed") and c["verification"] is None:
            warnings.append(f"{c['id']} ({c['label']}) has not been verified yet")
    for q in data["questions"]:
        if q["status"] == "open":
            warnings.append(f"{q['id']} is still open: {q['text']}")
        if q["status"] == "answered" and not q["evidence"]:
            errors.append(f"{q['id']} is marked answered without evidence")
        for e in q["evidence"]:
            if e not in claim_ids:
                errors.append(f"{q['id']} cites missing or retracted claim {e}")
    if not data["questions"]:
        warnings.append("no questions recorded; add the study checklist with 'question'")
    return errors, warnings


def cmd_check(a) -> None:
    data = load(Path(a.dir))
    errors, warnings = problems(data)
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"WARN    {w}")
    total_q = len(data["questions"])
    done = sum(1 for q in data["questions"] if q["status"] == "answered")
    retracted = len(data["claims"]) - len(live(data["claims"]))
    print(f"coverage: {done}/{total_q} questions answered; {len(live(data['claims']))} claims"
          f"{f' ({retracted} retracted)' if retracted else ''}; "
          f"{len(errors)} errors; {len(warnings)} warnings")
    if errors or (a.strict and warnings):
        sys.exit(1)


def md_escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def cmd_render(a) -> None:
    folder = Path(a.dir)
    data = load(folder)
    errors, warnings = problems(data)
    claims = live(data["claims"])
    gone = [c for c in data["claims"] if c.get("retracted")]
    by_label = {lab: sum(1 for c in claims if c["label"] == lab) for lab in LABELS}
    verified = sum(1 for c in claims if c["verification"] == "verified")
    qs = data["questions"]
    answered = sum(1 for q in qs if q["status"] == "answered")

    lines = [
        f"# Evidence: {data['subject']}",
        "",
        f"Kind: {data['kind']} · Created: {data['created'][:10]} · Updated: {data['updated'][:10]}",
        "",
        "## Summary",
        "",
        f"- Questions answered: **{answered}/{len(qs)}**",
        f"- Claims: **{len(claims)}** (" + ", ".join(f"{k} {v}" for k, v in by_label.items() if v) + ")",
        f"- Verified by an independent check: **{verified}**",
        f"- Problems: {len(errors)} errors, {len(warnings)} warnings",
        "",
        "## Coverage checklist",
        "",
        "| ID | Question | Status | Evidence | Note |",
        "| --- | --- | --- | --- | --- |",
    ]
    for q in qs:
        lines.append(
            f"| {q['id']} | {md_escape(q['text'])} | {q['status']} | {', '.join(q['evidence'])} | {md_escape(q['note'])} |"
        )
    lines += [
        "",
        "## Claims",
        "",
        "| ID | Claim | Label | Verified | Sources |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in claims:
        src = " ".join(f"[{i + 1}]({u})" for i, u in enumerate(c["sources"])) or "—"
        ver = c["verification"] or "—"
        if c["verification_note"]:
            ver += f": {md_escape(c['verification_note'])}"
        lines.append(f"| {c['id']} | {md_escape(c['text'])} | {c['label']} | {ver} | {src} |")
    if gone:
        lines += ["", "## Retracted claims", "", "| ID | Claim | Reason | Replaced by |", "| --- | --- | --- | --- |"]
        for c in gone:
            lines.append(f"| {c['id']} | ~~{md_escape(c['text'])}~~ | {md_escape(c.get('retracted_reason', ''))} | "
                         f"{', '.join(c.get('replaced_by', [])) or '—'} |")
    if errors or warnings:
        lines += ["", "## Open problems", ""]
        lines += [f"- ERROR: {e}" for e in errors]
        lines += [f"- {w}" for w in warnings]
    out = folder / "EVIDENCE.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


def all_ledgers(root: Path):
    for path in sorted(root.rglob(LEDGER)):
        try:
            with path.open(encoding="utf-8") as f:
                yield path.parent, json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"skipping {path}: {exc}", file=sys.stderr)


def cmd_index(a) -> None:
    root = Path(a.root)
    rows = []
    for folder, data in all_ledgers(root):
        qs = data.get("questions", [])
        answered = sum(1 for q in qs if q["status"] == "answered")
        rel = folder.relative_to(root).as_posix() or "."
        rows.append((data.get("kind", ""), data.get("subject", ""), rel, f"{answered}/{len(qs)}",
                     len(data.get("claims", [])), data.get("updated", "")[:10]))
    lines = [
        "# Blueprint knowledge index",
        "",
        "Every study and blueprint in this workspace. Reuse these before researching again.",
        "",
        "| Kind | Subject | Folder | Answered | Claims | Updated |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for r in sorted(rows):
        lines.append(f"| {r[0]} | {md_escape(r[1])} | `{r[2]}` | {r[3]} | {r[4]} | {r[5]} |")
    out = root / "INDEX.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(rows)} entries)")


def cmd_search(a) -> None:
    root = Path(a.root)
    term = a.term.lower()
    hits = 0
    for folder, data in all_ledgers(root):
        rel = folder.relative_to(root).as_posix() or "."
        for c in live(data.get("claims", [])):
            if term in c["text"].lower() or term in data.get("subject", "").lower():
                hits += 1
                ver = c.get("verification") or "unverified"
                print(f"{rel}#{c['id']} [{c['label']}, {ver}] {c['text']}")
                for s in c["sources"]:
                    print(f"    {s}")
    if not hits:
        print("no matches")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="RUB evidence ledger")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init"); s.add_argument("dir"); s.add_argument("--subject", required=True)
    s.add_argument("--kind", choices=KINDS, required=True); s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_init)

    s = sub.add_parser("question"); s.add_argument("dir"); s.add_argument("text"); s.set_defaults(fn=cmd_question)

    s = sub.add_parser("claim"); s.add_argument("dir"); s.add_argument("text")
    s.add_argument("--label", choices=LABELS, required=True)
    s.add_argument("--source", action="append")
    s.add_argument("--question", action="append", help="question IDs, repeat or comma-separate")
    s.add_argument("--by"); s.set_defaults(fn=cmd_claim)

    s = sub.add_parser("answer"); s.add_argument("dir"); s.add_argument("qid")
    s.add_argument("--status", choices=Q_STATUS[1:], required=True)
    s.add_argument("--evidence", action="append"); s.add_argument("--note"); s.set_defaults(fn=cmd_answer)

    s = sub.add_parser("verify"); s.add_argument("dir"); s.add_argument("eid")
    s.add_argument("--result", choices=V_RESULTS, required=True); s.add_argument("--note")
    s.set_defaults(fn=cmd_verify)

    s = sub.add_parser("retract"); s.add_argument("dir"); s.add_argument("eid")
    s.add_argument("--reason", required=True)
    s.add_argument("--replaced-by", action="append", help="claim IDs that replace it")
    s.set_defaults(fn=cmd_retract)

    s = sub.add_parser("check"); s.add_argument("dir"); s.add_argument("--strict", action="store_true")
    s.set_defaults(fn=cmd_check)

    s = sub.add_parser("render"); s.add_argument("dir"); s.set_defaults(fn=cmd_render)
    s = sub.add_parser("index"); s.add_argument("root"); s.set_defaults(fn=cmd_index)
    s = sub.add_parser("search"); s.add_argument("root"); s.add_argument("term"); s.set_defaults(fn=cmd_search)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
