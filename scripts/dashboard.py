#!/usr/bin/env python3
"""dashboard.py - one self-contained HTML page showing everything you have studied.

Usage:
  python dashboard.py <root> [--out FILE]

Scans <root> (default output: <root>/DASHBOARD.html) for:
  ledger.json  -> studies, with claims by label, verification results, open questions
  plan.json    -> go-to-market plans (target, phases, tasks)
  repomap.md / TOUR.md / LESSON.md / WALKTHROUGH.md / GTM.md / ROADMAP.html -> links to the documents
"""
import argparse, datetime as dt, html, json, os, sys
from pathlib import Path

DOCS = ("CASESTUDY.html", "LEARN-PLAN.html", "BUILD-PLAN.html", "LESSON.md", "BLUEPRINT.md", "TOUR.md", "WALKTHROUGH.md", "GTM.md", "ROADMAP.html", "EVIDENCE.md",
        "business.md", "explanation.md", "repomap.md", "playbook.md", "MATH.md")
SKIP = {".git", "node_modules", "__pycache__", "repo", ".venv"}


def esc(x):
    return html.escape(str(x))


def find(root: Path, name: str):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP]
        if name in files:
            yield Path(d)


def study_row(folder: Path, root: Path):
    try:
        data = json.loads((folder / "ledger.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    claims = [c for c in data.get("claims", []) if not c.get("retracted")]
    labels, ver = {}, {"verified": 0, "disputed": 0, "unverifiable": 0, "unchecked": 0}
    for c in claims:
        labels[c["label"]] = labels.get(c["label"], 0) + 1
        v = c.get("verification")
        v = v.get("result") if isinstance(v, dict) else v
        ver[v if v in ver else "unchecked"] += 1
    qs = data.get("questions", [])
    open_q = sum(1 for q in qs if q.get("status") in ("open", "partial"))
    docs = [d for d in DOCS if (folder / d).exists()]
    return {"folder": folder, "rel": os.path.relpath(folder, root), "subject": data.get("subject", folder.name),
            "kind": data.get("kind", ""), "updated": data.get("updated", "")[:10], "claims": len(claims),
            "labels": labels, "ver": ver, "questions": len(qs), "open": open_q, "docs": docs}


def plan_row(folder: Path, root: Path):
    try:
        p = json.loads((folder / "plan.json").read_text(encoding="utf-8"))
    except Exception:
        return None
    return {"rel": os.path.relpath(folder, root), "product": p.get("product", folder.name), "competitor": p.get("competitor", ""),
            "target": p.get("target_mrr"), "currency": p.get("currency", ""),
            "phases": [(ph.get("name"), ph.get("window", ""), ph.get("target_mrr"), len(ph.get("tasks", []))) for ph in p.get("phases", [])],
            "roadmap": (folder / "ROADMAP.html").exists()}


CSS = """
:root{--bg:#fbfaf7;--fg:#1f2430;--mut:#667085;--card:#fff;--line:#e4e1d8;--acc:#2f6f4f;--bad:#b42318;--warn:#b54708}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#14161a;--fg:#e8e6df;--mut:#9aa0ab;--card:#1c1f25;--line:#2d313a;--acc:#6fcf97;--bad:#f97066;--warn:#fdb022}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:28px 16px 60px}h1{margin:0 0 4px;font-size:26px}h2{margin:34px 0 10px;font-size:18px}
.sub{color:var(--mut);margin:0 0 22px}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px}
.stat,.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}.stat b{display:block;font-size:24px}
.stat span{color:var(--mut);font-size:13px}.card{margin-bottom:10px}.card h3{margin:0 0 2px;font-size:16px}.meta{color:var(--mut);font-size:13px}
.tags span{display:inline-block;margin:6px 6px 0 0;padding:2px 9px;border:1px solid var(--line);border-radius:999px;font-size:12px}
.bad{color:var(--bad)}.warn{color:var(--warn)}.ok{color:var(--acc)}a{color:var(--acc)}table{width:100%;border-collapse:collapse;font-size:14px}
td,th{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}.empty{color:var(--mut);padding:10px 0}
"""


def render(studies, plans, root):
    claims = sum(s["claims"] for s in studies)
    verified = sum(s["ver"]["verified"] for s in studies)
    disputed = sum(s["ver"]["disputed"] for s in studies)
    out = [f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>"
           f"<title>Blueprint Dashboard</title><style>{CSS}</style></head><body><main>",
           "<h1>RUB dashboard</h1>",
           f"<p class=sub>{esc(root)} &middot; built {dt.date.today().isoformat()}</p>",
           "<div class=stats>",
           f"<div class=stat><b>{len(studies)}</b><span>studies</span></div>",
           f"<div class=stat><b>{claims}</b><span>claims recorded</span></div>",
           f"<div class=stat><b class=ok>{verified}</b><span>verified</span></div>",
           f"<div class=stat><b class='{'bad' if disputed else ''}'>{disputed}</b><span>disputed</span></div>",
           f"<div class=stat><b>{len(plans)}</b><span>go-to-market plans</span></div></div>",
           "<h2>Studies</h2>"]
    if not studies:
        out.append("<p class=empty>No studies yet. Try /rub:explain, :startup or :opensource.</p>")
    for s in sorted(studies, key=lambda x: x["updated"], reverse=True):
        tags = "".join(f"<span>{esc(k)} {v}</span>" for k, v in sorted(s["labels"].items()))
        docs = " &middot; ".join(f"<a href='{esc(s['rel'])}/{esc(d)}'>{esc(d)}</a>" for d in s["docs"])
        flag = f" <span class=bad>&middot; {s['ver']['disputed']} disputed</span>" if s["ver"]["disputed"] else ""
        out.append(f"<div class=card><h3>{esc(s['subject'])}</h3><div class=meta>{esc(s['kind'])} &middot; updated {esc(s['updated'])} &middot; "
                   f"{s['claims']} claims ({s['ver']['verified']} verified, {s['ver']['unchecked']} unchecked){flag} &middot; "
                   f"{s['open']} of {s['questions']} questions still open</div><div class=tags>{tags}</div>"
                   f"<div class=meta style='margin-top:8px'>{docs}</div></div>")
    out.append("<h2>Go-to-market plans</h2>")
    if not plans:
        out.append("<p class=empty>No plans yet. Try /rub:launch.</p>")
    for p in plans:
        rows = "".join(f"<tr><td>{esc(n)}</td><td>{esc(w)}</td><td>{esc(p['currency'])}{esc(t)}</td><td>{k}</td></tr>" for n, w, t, k in p["phases"])
        link = f" &middot; <a href='{esc(p['rel'])}/ROADMAP.html'>open roadmap</a>" if p["roadmap"] else ""
        out.append(f"<div class=card><h3>{esc(p['product'])}</h3><div class=meta>learning from {esc(p['competitor'] or 'n/a')} &middot; "
                   f"target {esc(p['currency'])}{esc(p['target'])} MRR{link}</div>"
                   f"<table><tr><th>Phase<th>Window<th>MRR target<th>Tasks</tr>{rows}</table></div>")
    out.append("</main></body></html>")
    return "".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if not root.is_dir():
        sys.exit(f"not a folder: {root}")
    studies = [s for s in (study_row(f, root) for f in find(root, "ledger.json")) if s]
    plans = [p for p in (plan_row(f, root) for f in find(root, "plan.json")) if p]
    out = Path(a.out) if a.out else root / "DASHBOARD.html"
    out.write_text(render(studies, plans, root), encoding="utf-8")
    print(f"wrote {out} ({len(studies)} studies, {len(plans)} plans)")


if __name__ == "__main__":
    main()
