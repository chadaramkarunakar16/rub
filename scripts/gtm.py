#!/usr/bin/env python3
"""RUB go-to-market plan: MRR and funnel math, plus a visual roadmap.

A plan is a JSON file (see `template`). This tool:
  - checks it is complete and consistent
  - works out paying users per milestone, the new customers, trials and visitors needed each month
    (including churn), and the weekly hours the plan asks for
  - renders a self-contained HTML roadmap with tickable checklists (ticks are kept in the browser)

Commands
  template                 print an example plan
  check   <plan.json>      validate the plan
  math    <plan.json>      print the numbers (and write MATH.md next to the plan)
  render  <plan.json>      write ROADMAP.html and MATH.md next to the plan

Standard library only.
"""
from __future__ import annotations

import argparse
import html
import json
import math
import sys
from pathlib import Path

TEMPLATE = {
    "product": "Your product",
    "one_liner": "What it does, for whom",
    "competitor": "The competitor whose playbook you are learning from",
    "currency": "USD",
    "price_per_month": 9,
    "competitor_price": "Pro $15/mo, or $12/mo billed yearly",
    "target_mrr": 10000,
    "assumptions": {
        "monthly_churn": 0.05,
        "trial_to_paid": 0.15,
        "visitor_to_trial": 0.04,
        "notes": "Starting assumptions; replace with your own numbers once you have data. Cite benchmarks in the ledger."
    },
    "phases": [
        {
            "name": "Launch",
            "window": "Week 1-2",
            "months": 0.5,
            "target_mrr": 1000,
            "tasks": [
                {"task": "Free plan with a usage cap + 7-day trial of Pro", "learned_from": "Competitor: freemium",
                 "channel": "product", "hours_per_week": 2, "metric": "trial starts", "evidence": []}
            ]
        },
        {
            "name": "Grow",
            "window": "Month 1-3",
            "months": 2.5,
            "target_mrr": 5000,
            "tasks": [
                {"task": "Helpful posts in 3-5 niche communities, disclosing you're the maker",
                 "learned_from": "Competitor: Reddit", "channel": "community", "hours_per_week": 3,
                 "metric": "signups from community", "evidence": []}
            ]
        },
        {
            "name": "Scale",
            "window": "Month 4-6+",
            "months": 3,
            "target_mrr": 10000,
            "tasks": [
                {"task": "Creator affiliate programme: 30% recurring, $0 upfront",
                 "learned_from": "Competitor: creator affiliates", "channel": "partners", "hours_per_week": 2,
                 "metric": "affiliate signups", "evidence": []}
            ]
        }
    ]
}

SYMBOLS = {"USD": "$", "INR": "₹", "EUR": "€", "GBP": "£"}


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"error: {path} not found")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {path} is not valid JSON: {exc}")


def problems(plan: dict) -> list[str]:
    out = []
    for key in ("product", "price_per_month", "target_mrr", "phases"):
        if not plan.get(key):
            out.append(f"missing {key}")
    if out:
        return out
    price, target = plan["price_per_month"], plan["target_mrr"]
    if not isinstance(price, (int, float)) or price <= 0:
        out.append("price_per_month must be a positive number")
    if not isinstance(target, (int, float)) or target <= 0:
        out.append("target_mrr must be a positive number")
    a = plan.get("assumptions", {})
    for k in ("monthly_churn", "trial_to_paid", "visitor_to_trial"):
        v = a.get(k)
        if v is None:
            out.append(f"assumptions.{k} is missing")
        elif not isinstance(v, (int, float)) or not (0 < v < 1):
            out.append(f"assumptions.{k} must be between 0 and 1 (e.g. 0.05 for 5%)")
    prev = 0
    for i, ph in enumerate(plan["phases"], 1):
        label = ph.get("name") or f"phase {i}"
        if not ph.get("name"):
            out.append(f"phase {i} needs a name")
        m = ph.get("months")
        if not isinstance(m, (int, float)) or m <= 0:
            out.append(f"{label}: months must be a positive number (0.5 = two weeks)")
        t = ph.get("target_mrr")
        if not isinstance(t, (int, float)) or t <= prev:
            out.append(f"{label}: target_mrr must be higher than the previous phase ({prev})")
        else:
            prev = t
        tasks = ph.get("tasks") or []
        if not tasks:
            out.append(f"{label}: add at least one task")
        for j, task in enumerate(tasks, 1):
            if not task.get("task"):
                out.append(f"{label} task {j}: missing 'task'")
            if not task.get("learned_from"):
                out.append(f"{label} task {j}: say what it is 'learned_from' (or 'Our idea')")
            h = task.get("hours_per_week", 0)
            if not isinstance(h, (int, float)) or h < 0:
                out.append(f"{label} task {j}: hours_per_week must be 0 or more")
    if isinstance(target, (int, float)) and plan["phases"] and plan["phases"][-1].get("target_mrr") != target:
        out.append("the last phase's target_mrr should equal target_mrr")
    return out


def compute(plan: dict) -> dict:
    price = float(plan["price_per_month"])
    a = plan["assumptions"]
    churn, t2p, v2t = a["monthly_churn"], a["trial_to_paid"], a["visitor_to_trial"]
    rows = []
    start_mrr = 0.0
    elapsed = 0.0
    for ph in plan["phases"]:
        months = float(ph["months"])
        end_mrr = float(ph["target_mrr"])
        start_users = math.ceil(start_mrr / price)
        end_users = math.ceil(end_mrr / price)
        net_per_month = (end_users - start_users) / months
        churned_per_month = churn * (start_users + end_users) / 2
        new_paid = net_per_month + churned_per_month
        trials = new_paid / t2p
        visitors = trials / v2t
        hours = sum(float(t.get("hours_per_week", 0)) for t in ph["tasks"])
        elapsed += months
        rows.append({
            "phase": ph["name"], "window": ph.get("window", ""), "months": months, "ends_month": elapsed,
            "start_mrr": start_mrr, "end_mrr": end_mrr, "start_users": start_users, "end_users": end_users,
            "net_new_paid_per_month": net_per_month, "churned_per_month": churned_per_month,
            "new_paid_per_month": new_paid, "trials_per_month": trials, "visitors_per_month": visitors,
            "hours_per_week": hours,
        })
        start_mrr = end_mrr
    return {
        "price": price, "target_mrr": float(plan["target_mrr"]),
        "target_users": math.ceil(float(plan["target_mrr"]) / price),
        "arr_at_target": float(plan["target_mrr"]) * 12, "total_months": elapsed,
        "steady_state_new_paid_per_month": math.ceil(float(plan["target_mrr"]) / price) * churn,
        "rows": rows,
    }


def fmt_money(v: float, cur: str) -> str:
    sym = SYMBOLS.get(cur.upper(), cur + " ")
    if v >= 1e7 and cur.upper() == "INR":
        return f"{sym}{v / 1e7:.2f} Cr"
    if v >= 1e5 and cur.upper() == "INR":
        return f"{sym}{v / 1e5:.2f} L"
    if v >= 1e6:
        return f"{sym}{v / 1e6:.2f}M"
    if v >= 1e3:
        return f"{sym}{v / 1e3:.1f}k".replace(".0k", "k")
    return f"{sym}{v:,.0f}"


def math_markdown(plan: dict, r: dict) -> str:
    cur = plan.get("currency", "USD")
    a = plan["assumptions"]
    lines = [
        f"# The numbers: {plan['product']} to {fmt_money(r['target_mrr'], cur)} MRR",
        "",
        f"Price {fmt_money(r['price'], cur)}/month → **{r['target_users']:,} paying users** for "
        f"{fmt_money(r['target_mrr'], cur)} MRR ({fmt_money(r['arr_at_target'], cur)} ARR), "
        f"planned over about {r['total_months']:g} months.",
        "",
        f"Assumptions (estimates until you have data): monthly churn {a['monthly_churn']:.0%}, "
        f"trial → paid {a['trial_to_paid']:.0%}, visitor → trial {a['visitor_to_trial']:.0%}.",
        "",
        "| Phase | Window | MRR | Paying users | New paid / month (incl. churn) | Trials / month | Visitors / month | Your hours / week |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in r["rows"]:
        lines.append(
            f"| {row['phase']} | {row['window']} | {fmt_money(row['start_mrr'], cur)} → {fmt_money(row['end_mrr'], cur)} | "
            f"{row['start_users']:,} → {row['end_users']:,} | {math.ceil(row['new_paid_per_month']):,} | "
            f"{math.ceil(row['trials_per_month']):,} | {math.ceil(row['visitors_per_month']):,} | {row['hours_per_week']:g} |"
        )
    lines += [
        "",
        f"At {fmt_money(r['target_mrr'], cur)} MRR you lose about **{math.ceil(r['steady_state_new_paid_per_month']):,} "
        f"customers a month** to churn, so growth must keep bringing in at least that many just to stay level.",
        "",
        "How to read this: new paid per month = (users to add ÷ months) + users lost to churn. Trials = new paid ÷ "
        "trial→paid rate. Visitors = trials ÷ visitor→trial rate. Lower churn or better conversion shrinks every "
        "number after it; that is usually cheaper than more traffic.",
    ]
    return "\n".join(lines) + "\n"


CSS = """
:root{--bg:#0f1115;--panel:#161a20;--line:#2a313b;--text:#e8ecf1;--muted:#9aa4b2;--accent:#2fbf71;--accent-2:#1f8f53;--box:#1b2028;--tick:#2fbf71}
@media (prefers-color-scheme: light){:root:not([data-theme="dark"]){--bg:#f6f7f9;--panel:#ffffff;--line:#d6dbe2;--text:#14181f;--muted:#5b6573;--accent:#178a4c;--accent-2:#11703c;--box:#f0f3f6;--tick:#178a4c}}
:root[data-theme="dark"]{--bg:#0f1115;--panel:#161a20;--line:#2a313b;--text:#e8ecf1;--muted:#9aa4b2;--accent:#2fbf71;--accent-2:#1f8f53;--box:#1b2028;--tick:#2fbf71}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 16px 48px}
h1{font-size:clamp(22px,3.2vw,32px);margin:0 0 6px}.sub{color:var(--accent);margin:0 0 24px;font-size:14px}
.ms{display:flex;align-items:stretch;gap:0;flex-wrap:wrap;margin-bottom:28px}
.m{flex:1 1 160px;border:1.5px solid var(--accent);background:var(--panel);border-radius:10px;padding:14px;text-align:center;min-width:140px}
.m:first-child{border-color:var(--line)}.m b{display:block;font-size:18px}.m span{color:var(--muted);font-size:13px}
.arrow{flex:0 0 34px;display:flex;align-items:center;justify-content:center;color:var(--accent);font-size:22px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px}
.ph h2{margin:0 0 12px;font-size:15px;text-align:center;border:1.5px solid var(--accent);background:var(--accent-2);color:#fff;border-radius:8px;padding:10px}
.ph .meta{color:var(--muted);font-size:12px;text-align:center;margin:-6px 0 10px}
.t{display:flex;gap:10px;align-items:flex-start;border:1.5px solid var(--accent-2);background:var(--box);border-radius:9px;padding:11px 12px;margin-bottom:10px;cursor:pointer}
.t input{margin-top:3px;accent-color:var(--tick);width:16px;height:16px;flex:0 0 auto}
.t .from{display:block;color:var(--muted);font-size:12px;margin-top:3px}
.t.done .txt{text-decoration:line-through;color:var(--muted)}
.prog{color:var(--muted);font-size:13px;margin:6px 0 22px}
table{width:100%;border-collapse:collapse;margin-top:26px;font-size:13px;background:var(--panel);border-radius:8px;overflow:hidden}
th,td{border-bottom:1px solid var(--line);padding:8px 10px;text-align:left}th{color:var(--muted);font-weight:600}
.scroll{overflow-x:auto}.note{color:var(--muted);font-size:12.5px;margin-top:10px}
@media (max-width:700px){.ms{flex-direction:column}.m{flex:0 0 auto}.arrow{flex:0 0 26px;transform:rotate(90deg)}}
"""

JS = """
(function(){
  var key='gtm-roadmap:'+document.title;
  var state={};
  try{state=JSON.parse(localStorage.getItem(key)||'{}')||{};}catch(e){state={};}
  var boxes=document.querySelectorAll('.t input');
  function save(){try{localStorage.setItem(key,JSON.stringify(state));}catch(e){}}
  function progress(){var n=0;boxes.forEach(function(b){if(b.checked)n++;});
    document.getElementById('prog').textContent=n+' of '+boxes.length+' tasks done';}
  boxes.forEach(function(b){
    b.checked=!!state[b.id]; b.closest('.t').classList.toggle('done',b.checked);
    b.addEventListener('change',function(){state[b.id]=b.checked;b.closest('.t').classList.toggle('done',b.checked);save();progress();});
  });
  progress();
})();
"""


def render_html(plan: dict, r: dict) -> str:
    cur = plan.get("currency", "USD")
    e = html.escape
    title = f"Plan: {plan['product']} to {fmt_money(r['target_mrr'], cur)} MRR"
    sub = f"Price {fmt_money(r['price'], cur)}/mo"
    if plan.get("competitor_price"):
        sub += f" ({plan.get('competitor', 'competitor')}: {plan['competitor_price']})"
    if plan.get("competitor"):
        sub += f" · learning from {plan['competitor']}'s playbook"

    ms = [f'<div class="m"><b>Today</b><span>{fmt_money(0, cur)} MRR</span></div>']
    for row in r["rows"]:
        ms.append('<div class="arrow" aria-hidden="true">→</div>')
        ms.append(f'<div class="m"><b>{fmt_money(row["end_mrr"], cur)} MRR</b>'
                  f'<span>{row["end_users"]:,} paying users</span></div>')

    cols = []
    for i, (ph, row) in enumerate(zip(plan["phases"], r["rows"]), 1):
        tasks = []
        for j, t in enumerate(ph["tasks"], 1):
            tid = f"t{i}-{j}"
            extra = []
            if t.get("hours_per_week"):
                extra.append(f"~{t['hours_per_week']:g} h/week")
            if t.get("metric"):
                extra.append(f"track: {e(str(t['metric']))}")
            if t.get("evidence"):
                extra.append(" ".join(f"[{e(str(x))}]" for x in t["evidence"]))
            from_line = f"({e(t['learned_from'])})" + (f" · {' · '.join(extra)}" if extra else "")
            tasks.append(f'<label class="t" for="{tid}"><input type="checkbox" id="{tid}">'
                         f'<span><span class="txt">{e(t["task"])}</span><span class="from">{from_line}</span></span></label>')
        cols.append(
            f'<section class="ph"><h2>{i}. {e(ph["name"].upper())} ({e(ph.get("window", ""))}) → '
            f'{fmt_money(row["end_mrr"], cur)}</h2>'
            f'<div class="meta">~{math.ceil(row["new_paid_per_month"]):,} new paying users/month · '
            f'{row["hours_per_week"]:g} h/week</div>' + "".join(tasks) + "</section>")

    trs = "".join(
        f"<tr><td>{e(row['phase'])}</td><td>{fmt_money(row['start_mrr'], cur)} → {fmt_money(row['end_mrr'], cur)}</td>"
        f"<td>{row['start_users']:,} → {row['end_users']:,}</td><td>{math.ceil(row['new_paid_per_month']):,}</td>"
        f"<td>{math.ceil(row['trials_per_month']):,}</td><td>{math.ceil(row['visitors_per_month']):,}</td></tr>"
        for row in r["rows"])
    a = plan["assumptions"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title><style>{CSS}</style></head>
<body><div class="wrap"><h1>{e(title)}</h1><p class="sub">{e(sub)}</p>
<div class="ms">{''.join(ms)}</div><div class="prog" id="prog"></div>
<div class="cols">{''.join(cols)}</div>
<div class="scroll"><table><thead><tr><th>Phase</th><th>MRR</th><th>Paying users</th><th>New paid / month</th>
<th>Trials / month</th><th>Visitors / month</th></tr></thead><tbody>{trs}</tbody></table></div>
<p class="note">Estimates from assumptions: churn {a['monthly_churn']:.0%}/month, trial→paid {a['trial_to_paid']:.0%},
visitor→trial {a['visitor_to_trial']:.0%}. New paid per month includes replacing churned users. Replace with your real
numbers as data comes in. Ticks are saved in this browser only.</p></div><script>{JS}</script></body></html>"""


def checked(path: Path) -> dict:
    plan = load(path)
    ps = problems(plan)
    if ps:
        for p in ps:
            print(f"ERROR   {p}")
        sys.exit(1)
    return plan


def cmd_template(_a) -> int:
    print(json.dumps(TEMPLATE, indent=2, ensure_ascii=False))
    return 0


def cmd_check(a) -> int:
    checked(Path(a.plan))
    print("plan is valid")
    return 0


def cmd_math(a) -> int:
    path = Path(a.plan)
    plan = checked(path)
    md = math_markdown(plan, compute(plan))
    (path.parent / "MATH.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


def cmd_render(a) -> int:
    path = Path(a.plan)
    plan = checked(path)
    r = compute(plan)
    (path.parent / "MATH.md").write_text(math_markdown(plan, r), encoding="utf-8")
    out = path.parent / "ROADMAP.html"
    out.write_text(render_html(plan, r), encoding="utf-8")
    print(f"wrote {out} and {path.parent / 'MATH.md'}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Go-to-market plan math and roadmap")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("template").set_defaults(fn=cmd_template)
    for name, fn in (("check", cmd_check), ("math", cmd_math), ("render", cmd_render)):
        s = sub.add_parser(name); s.add_argument("plan"); s.set_defaults(fn=fn)
    a = p.parse_args(argv)
    return a.fn(a) or 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
