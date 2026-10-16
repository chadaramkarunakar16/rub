#!/usr/bin/env python3
"""RUB startup dataset.

A scan folder holds one JSON record per company in <scan>/companies/<slug>.json.
This tool validates them, merges them into a CSV, computes breakdowns, and filters.

Commands
  template                     print an empty company record
  validate <scan>              check every record against the schema
  merge    <scan>              write <scan>/companies.csv and <scan>/SUMMARY.md
  query    <scan> [--where field=value ...] [--sort field] [--limit N]
  combine  <root>              merge every scan under <root> into <root>/_all/companies.csv + SUMMARY.md

Standard library only. Works on Windows, macOS and Linux.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

CUSTOMER_TYPES = ("b2b", "b2c", "b2b2c", "developer", "government", "marketplace")
BUSINESS_MODELS = ("subscription", "usage", "transaction", "marketplace", "services",
                   "advertising", "license", "hardware", "hybrid", "unknown")
STAGES = ("pre-seed", "seed", "series-a", "series-b", "series-c", "series-d+", "growth",
          "grant", "unknown")

TEMPLATE = {
    "name": "",
    "slug": "",
    "website": "",
    "one_liner": "",
    "problem": "",
    "customer": "",
    "customer_type": "b2b",
    "category": "",
    "ai_native": True,
    "business_model": "subscription",
    "pricing": "",
    "yc_batch": "",
    "hq": "",
    "founded": None,
    "team_size": None,
    "funding_total_usd": None,
    "last_round": {"stage": "unknown", "amount_usd": None, "date": "", "lead_investors": []},
    "traction_signals": [],
    "why_funded": "",
    "growth_engine": "",
    "moat": "",
    "india_angle": "",
    "sources": [],
    "researched_at": "",
}

REQUIRED = ("name", "slug", "one_liner", "problem", "customer_type", "category", "business_model", "sources")

CSV_FIELDS = ["name", "slug", "website", "one_liner", "problem", "customer", "customer_type", "category",
              "ai_native", "business_model", "pricing", "yc_batch", "hq", "founded", "team_size",
              "funding_total_usd", "last_round_stage", "last_round_amount_usd", "last_round_date",
              "lead_investors", "traction_signals", "why_funded", "growth_engine", "moat", "india_angle",
              "sources", "researched_at", "scan"]


def records(scan: Path):
    folder = scan / "companies"
    if not folder.is_dir():
        sys.exit(f"error: {folder} does not exist")
    for path in sorted(folder.glob("*.json")):
        try:
            with path.open(encoding="utf-8") as f:
                yield path, json.load(f)
        except json.JSONDecodeError as exc:
            yield path, {"__error__": f"invalid JSON: {exc}"}


def problems(rec: dict, path: Path) -> list[str]:
    if "__error__" in rec:
        return [rec["__error__"]]
    out = []
    for field in REQUIRED:
        if not rec.get(field):
            out.append(f"missing {field}")
    if rec.get("slug") and rec["slug"] != path.stem:
        out.append(f"slug '{rec['slug']}' does not match file name '{path.stem}'")
    if rec.get("customer_type") and rec["customer_type"] not in CUSTOMER_TYPES:
        out.append(f"customer_type must be one of {', '.join(CUSTOMER_TYPES)}")
    if rec.get("business_model") and rec["business_model"] not in BUSINESS_MODELS:
        out.append(f"business_model must be one of {', '.join(BUSINESS_MODELS)}")
    stage = (rec.get("last_round") or {}).get("stage", "unknown")
    if stage not in STAGES:
        out.append(f"last_round.stage must be one of {', '.join(STAGES)}")
    for key in ("funding_total_usd",):
        v = rec.get(key)
        if v is not None and not isinstance(v, (int, float)):
            out.append(f"{key} must be a number (USD) or null")
    amt = (rec.get("last_round") or {}).get("amount_usd")
    if amt is not None and not isinstance(amt, (int, float)):
        out.append("last_round.amount_usd must be a number (USD) or null")
    date = (rec.get("last_round") or {}).get("date", "")
    if date:
        try:
            dt.date.fromisoformat(date[:10] if len(date) >= 10 else date + "-01" if len(date) == 7 else date)
        except ValueError:
            out.append("last_round.date must be YYYY-MM-DD or YYYY-MM")
    for s in rec.get("sources", []):
        if not str(s).startswith(("http://", "https://")):
            out.append(f"source is not a URL: {s}")
    if rec.get("funding_total_usd") and not rec.get("sources"):
        out.append("funding figures need sources")
    return out


def cmd_template(_a) -> None:
    print(json.dumps(TEMPLATE, indent=2))


def cmd_validate(a) -> int:
    bad = 0
    n = 0
    for path, rec in records(Path(a.scan)):
        n += 1
        ps = problems(rec, path)
        if ps:
            bad += 1
            for p in ps:
                print(f"{path.name}: {p}")
    print(f"{n} records, {n - bad} valid, {bad} with problems")
    return 1 if bad else 0


def flatten(rec: dict, scan_name: str) -> dict:
    lr = rec.get("last_round") or {}
    return {
        **{k: rec.get(k, "") for k in CSV_FIELDS if k in TEMPLATE},
        "ai_native": "yes" if rec.get("ai_native") else "no",
        "last_round_stage": lr.get("stage", ""),
        "last_round_amount_usd": lr.get("amount_usd") if lr.get("amount_usd") is not None else "",
        "last_round_date": lr.get("date", ""),
        "lead_investors": "; ".join(lr.get("lead_investors", [])),
        "traction_signals": "; ".join(rec.get("traction_signals", [])),
        "sources": " ".join(rec.get("sources", [])),
        "funding_total_usd": rec.get("funding_total_usd") if rec.get("funding_total_usd") is not None else "",
        "founded": rec.get("founded") or "",
        "team_size": rec.get("team_size") or "",
        "scan": scan_name,
    }


def money(v) -> str:
    if v in ("", None):
        return "n/a"
    v = float(v)
    for unit, div in (("B", 1e9), ("M", 1e6), ("K", 1e3)):
        if v >= div:
            return f"${v / div:.1f}{unit}"
    return f"${v:,.0f}"


def breakdown(rows: list[dict], field: str, title: str) -> list[str]:
    c = Counter((r[field] or "unknown") for r in rows)
    total = len(rows) or 1
    lines = [f"### {title}", "", f"| {field} | companies | share |", "| --- | --- | --- |"]
    for k, v in c.most_common():
        lines.append(f"| {k} | {v} | {v * 100 / total:.0f}% |")
    return lines + [""]


def write_outputs(rows: list[dict], out_dir: Path, title: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "companies.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        w.writerows(rows)

    funded = [float(r["funding_total_usd"]) for r in rows if r["funding_total_usd"] not in ("", None)]
    rounds = [r for r in rows if r["last_round_amount_usd"] not in ("", None)]
    lines = [
        f"# {title}",
        "",
        f"Generated {dt.date.today().isoformat()} from {len(rows)} company records.",
        "",
        "## Funding",
        "",
        f"- Companies with disclosed total funding: **{len(funded)}** of {len(rows)}",
    ]
    if funded:
        lines += [
            f"- Total disclosed: **{money(sum(funded))}**",
            f"- Median per company: **{money(statistics.median(funded))}**",
        ]
    lines.append("")
    lines += breakdown(rows, "category", "By category")
    lines += breakdown(rows, "business_model", "By business model")
    lines += breakdown(rows, "customer_type", "By customer type")
    lines += breakdown(rows, "last_round_stage", "By latest round stage")
    if any(r["yc_batch"] for r in rows):
        lines += breakdown(rows, "yc_batch", "By YC batch")
    ai = sum(1 for r in rows if r["ai_native"] == "yes")
    lines += [f"AI-native: **{ai}** of {len(rows)}", ""]

    if rounds:
        lines += ["## Largest latest rounds", "", "| Company | Stage | Amount | Date | Lead investors |",
                  "| --- | --- | --- | --- | --- |"]
        for r in sorted(rounds, key=lambda r: float(r["last_round_amount_usd"]), reverse=True)[:15]:
            lines.append(f"| {r['name']} | {r['last_round_stage']} | {money(r['last_round_amount_usd'])} | "
                         f"{r['last_round_date']} | {r['lead_investors']} |")
        lines.append("")
    inv = Counter(i.strip() for r in rows for i in r["lead_investors"].split(";") if i.strip())
    if inv:
        lines += ["## Most frequent lead investors", "", "| Investor | Rounds led |", "| --- | --- |"]
        lines += [f"| {k} | {v} |" for k, v in inv.most_common(10)]
        lines.append("")
    lines += ["## Companies", "", "| Company | One-liner | Customer | Model | Category |",
              "| --- | --- | --- | --- | --- |"]
    for r in sorted(rows, key=lambda r: r["name"].lower()):
        one = str(r["one_liner"]).replace("|", "\\|")
        lines.append(f"| {r['name']} | {one} | {r['customer_type']} | {r['business_model']} | {r['category']} |")
    (out_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out_dir / 'companies.csv'} and {out_dir / 'SUMMARY.md'} ({len(rows)} companies)")


def valid_rows(scan: Path) -> list[dict]:
    rows = []
    for path, rec in records(scan):
        ps = problems(rec, path)
        if ps:
            print(f"skipping {path.name}: {'; '.join(ps)}", file=sys.stderr)
            continue
        rows.append(flatten(rec, scan.name))
    return rows


def cmd_merge(a) -> int:
    scan = Path(a.scan)
    write_outputs(valid_rows(scan), scan, f"Scan: {scan.name}")
    return 0


def cmd_combine(a) -> int:
    root = Path(a.root)
    rows: dict[str, dict] = {}
    for comp in sorted(root.rglob("companies")):
        if comp.is_dir() and comp.parent.name != "_all":
            for r in valid_rows(comp.parent):
                prev = rows.get(r["slug"])
                # keep the most recently researched record for each company
                if prev is None or r["researched_at"] >= prev["researched_at"]:
                    rows[r["slug"]] = r
    write_outputs(list(rows.values()), root / "_all", "All scanned companies")
    return 0


def cmd_query(a) -> int:
    scan = Path(a.scan)
    csv_path = scan / "companies.csv"
    if not csv_path.exists():
        sys.exit(f"error: run 'merge' first ({csv_path} missing)")
    with csv_path.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for cond in a.where or []:
        if "=" not in cond:
            sys.exit(f"error: --where needs field=value, got {cond}")
        k, v = cond.split("=", 1)
        if k not in CSV_FIELDS:
            sys.exit(f"error: unknown field {k}")
        rows = [r for r in rows if v.lower() in str(r[k]).lower()]
    if a.sort:
        if a.sort not in CSV_FIELDS:
            sys.exit(f"error: unknown field {a.sort}")
        def as_num(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        numeric = [r for r in rows if as_num(r[a.sort]) is not None]
        if numeric:
            # numbers high to low; blanks and text after them
            rest = [r for r in rows if as_num(r[a.sort]) is None]
            rows = sorted(numeric, key=lambda r: as_num(r[a.sort]), reverse=True) + rest
        else:
            rows.sort(key=lambda r: str(r[a.sort]).lower())
    for r in rows[: a.limit]:
        amt = money(r["last_round_amount_usd"]) if r["last_round_amount_usd"] else "n/a"
        print(f"{r['name']:<24} {r['category']:<22} {r['business_model']:<13} {r['last_round_stage']:<10} "
              f"{amt:>9}  {r['one_liner']}")
    print(f"({len(rows)} matching)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="RUB startup dataset")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template").set_defaults(fn=cmd_template)
    s = sub.add_parser("validate"); s.add_argument("scan"); s.set_defaults(fn=cmd_validate)
    s = sub.add_parser("merge"); s.add_argument("scan"); s.set_defaults(fn=cmd_merge)
    s = sub.add_parser("combine"); s.add_argument("root"); s.set_defaults(fn=cmd_combine)
    s = sub.add_parser("query"); s.add_argument("scan"); s.add_argument("--where", action="append")
    s.add_argument("--sort"); s.add_argument("--limit", type=int, default=50); s.set_defaults(fn=cmd_query)
    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
