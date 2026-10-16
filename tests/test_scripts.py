"""Tests for the RUB scripts. Run: python -m pytest tests -q"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "scripts"


def run(script, *args, ok=True):
    r = subprocess.run([sys.executable, str(S / script), *map(str, args)], capture_output=True, text=True)
    if ok:
        assert r.returncode == 0, f"{script} {args}\n{r.stdout}\n{r.stderr}"
    return r


# ---------- ledger ----------

@pytest.fixture
def study(tmp_path):
    d = tmp_path / "study"
    run("ledger.py", "init", d, "--subject", "Demo", "--kind", "feature")
    return d


def test_ledger_init_kinds(tmp_path):
    for kind in ("feature", "product", "category", "build", "plan", "repo"):
        run("ledger.py", "init", tmp_path / kind, "--subject", "x", "--kind", kind)
    assert run("ledger.py", "init", tmp_path / "bad", "--subject", "x", "--kind", "nope", ok=False).returncode != 0


def test_claim_needs_source_when_confirmed(study):
    r = run("ledger.py", "claim", study, "It uses WebSockets", "--label", "confirmed", ok=False)
    assert r.returncode != 0 and "source" in r.stderr


def test_claim_rejects_bad_source(study):
    r = run("ledger.py", "claim", study, "x", "--label", "confirmed", "--source", "my memory", ok=False)
    assert r.returncode != 0


def test_pattern_claim_needs_no_source(study):
    r = run("ledger.py", "claim", study, "Common approach", "--label", "pattern")
    assert r.stdout.strip() == "E1"


def test_question_answer_verify_flow(study):
    q = run("ledger.py", "question", study, "How does sync work?").stdout.strip()
    e = run("ledger.py", "claim", study, "Uses CRDTs", "--label", "confirmed", "--source", "https://example.com/blog",
            "--question", q).stdout.strip()
    run("ledger.py", "answer", study, q, "--status", "answered", "--evidence", e)
    run("ledger.py", "verify", study, e, "--result", "verified", "--note", "checked page")
    run("ledger.py", "check", study)
    data = json.loads((study / "ledger.json").read_text())
    assert data["claims"][0]["verification"] == "verified"
    assert data["questions"][0]["status"] == "answered"


def test_disputed_claim_fails_check_until_retracted(study):
    e = run("ledger.py", "claim", study, "Wrong", "--label", "confirmed", "--source", "https://example.com").stdout.strip()
    run("ledger.py", "verify", study, e, "--result", "disputed", "--note", "page says otherwise")
    assert run("ledger.py", "check", study, ok=False).returncode != 0
    e2 = run("ledger.py", "claim", study, "Right", "--label", "confirmed", "--source", "https://example.com").stdout.strip()
    run("ledger.py", "retract", study, e, "--reason", "wrong", "--replaced-by", e2)
    run("ledger.py", "verify", study, e2, "--result", "verified")
    run("ledger.py", "check", study)


def test_unchecked_confirmed_claim_warns_and_fails_only_in_strict(study):
    run("ledger.py", "claim", study, "Needs checking", "--label", "confirmed", "--source", "https://example.com")
    r = run("ledger.py", "check", study)
    assert "has not been verified" in r.stdout
    assert run("ledger.py", "check", study, "--strict", ok=False).returncode != 0


def test_render_index_search(tmp_path, study):
    run("ledger.py", "claim", study, "Uses Postgres", "--label", "pattern")
    run("ledger.py", "render", study)
    assert (study / "EVIDENCE.md").exists()
    run("ledger.py", "index", tmp_path)
    assert (tmp_path / "INDEX.md").exists()
    assert "Postgres" in run("ledger.py", "search", tmp_path, "postgres").stdout


# ---------- dataset ----------

def test_dataset_template_validate_query(tmp_path):
    tpl = run("dataset.py", "template").stdout
    data = json.loads(tpl)
    assert data  # template is valid JSON
    scan = tmp_path / "scan"
    scan.mkdir()
    (scan / "startups.json").write_text(tpl, encoding="utf-8")
    r = run("dataset.py", "validate", scan, ok=False)
    assert r.returncode in (0, 1)  # template placeholders may or may not pass; must not crash
    assert "Traceback" not in r.stderr


# ---------- snapshot ----------

def test_snapshot_path_and_list(tmp_path):
    p = run("snapshot.py", "path", tmp_path, "pricing").stdout.strip()
    assert "snapshots" in p and "pricing" in p
    run("snapshot.py", "list", tmp_path)


# ---------- gtm ----------

def make_plan(tmp_path, **over):
    plan = json.loads(run("gtm.py", "template").stdout)
    plan.update(over)
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(plan), encoding="utf-8")
    return f


def test_gtm_template_checks_and_renders(tmp_path):
    f = make_plan(tmp_path)
    run("gtm.py", "check", f)
    run("gtm.py", "render", f)
    html = (tmp_path / "ROADMAP.html").read_text(encoding="utf-8")
    assert "<html" in html and (tmp_path / "MATH.md").exists()
    assert "http://" not in html.replace("http://www.w3.org", "")  # self-contained


def test_gtm_rejects_bad_churn(tmp_path):
    plan = json.loads(run("gtm.py", "template").stdout)
    plan["assumptions"]["monthly_churn"] = 1.5
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(plan), encoding="utf-8")
    assert run("gtm.py", "check", f, ok=False).returncode != 0


def test_gtm_rejects_last_phase_not_target(tmp_path):
    plan = json.loads(run("gtm.py", "template").stdout)
    plan["target_mrr"] = plan["target_mrr"] * 3
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(plan), encoding="utf-8")
    assert run("gtm.py", "check", f, ok=False).returncode != 0


def test_gtm_rejects_task_without_source(tmp_path):
    plan = json.loads(run("gtm.py", "template").stdout)
    del plan["phases"][0]["tasks"][0]["learned_from"]
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(plan), encoding="utf-8")
    assert run("gtm.py", "check", f, ok=False).returncode != 0


def test_gtm_math_paying_users(tmp_path):
    f = make_plan(tmp_path, price_per_month=10, target_mrr=10000)
    out = run("gtm.py", "math", f).stdout
    assert "1,000" in out or "1000" in out  # 10,000 / 10 = 1,000 paying users at the target


def test_gtm_escapes_html(tmp_path):
    plan = json.loads(run("gtm.py", "template").stdout)
    plan["product"] = "<script>alert(1)</script>"
    f = tmp_path / "plan.json"
    f.write_text(json.dumps(plan), encoding="utf-8")
    run("gtm.py", "render", f)
    assert "<script>alert(1)</script>" not in (tmp_path / "ROADMAP.html").read_text(encoding="utf-8")


# ---------- repomap ----------

def test_repomap_detects_stack_and_license(tmp_path):
    repo = tmp_path / "r"
    (repo / "src").mkdir(parents=True)
    (repo / "package.json").write_text(json.dumps({"dependencies": {"react": "1", "express": "4", "stripe": "1"}}))
    (repo / "src" / "server.ts").write_text("console.log(1)\n")
    (repo / "LICENSE").write_text("MIT License\n\nPermission is hereby granted, free of charge, to any person")
    out = run("repomap.py", "map", repo, "--json").stdout
    m = json.loads(out)
    assert m["license"] == "MIT"
    assert {"React", "Express", "Stripe payments"} <= set(m["stack"])
    assert "src/server.ts" in m["entry_points"]
    assert m["languages"]["TypeScript"] == 1


def test_repomap_skips_node_modules(tmp_path):
    repo = tmp_path / "r"
    (repo / "node_modules" / "x").mkdir(parents=True)
    (repo / "node_modules" / "x" / "a.js").write_text("x")
    (repo / "main.py").write_text("print(1)\n")
    m = json.loads(run("repomap.py", "map", repo, "--json").stdout)
    assert m["files"] == 1


def test_repomap_no_license(tmp_path):
    (tmp_path / "a.py").write_text("x=1\n")
    assert json.loads(run("repomap.py", "map", tmp_path, "--json").stdout)["license"] == "none found"


# ---------- dashboard ----------

def test_dashboard_lists_studies_and_plans(tmp_path):
    s = tmp_path / "studies" / "demo"
    run("ledger.py", "init", s, "--subject", "Demo <b>study</b>", "--kind", "product")
    run("ledger.py", "claim", s, "A pattern", "--label", "pattern")
    g = tmp_path / "studies" / "demo" / "gtm"
    g.mkdir()
    (g / "plan.json").write_text(run("gtm.py", "template").stdout, encoding="utf-8")
    run("dashboard.py", tmp_path)
    page = (tmp_path / "DASHBOARD.html").read_text(encoding="utf-8")
    assert "Demo &lt;b&gt;study&lt;/b&gt;" in page and "<b>study</b>" not in page
    assert "Go-to-market plans" in page


def test_dashboard_empty_folder(tmp_path):
    run("dashboard.py", tmp_path)
    assert "No studies yet" in (tmp_path / "DASHBOARD.html").read_text(encoding="utf-8")


# ---------- doctor / plugin integrity ----------

def test_doctor_passes_on_this_plugin():
    r = run("doctor.py", "--offline")
    assert "0 failed" in r.stdout


def test_every_skill_has_description_and_unique_name():
    names = []
    for p in (ROOT / "skills").glob("*/SKILL.md"):
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---\n") and "\ndescription:" in text, p
        names.append(p.parent.name)
    assert len(names) == len(set(names)) >= 16


# ---------- rubdoc (case study, learn plan, build plan) ----------

def doc_json(tmp_path, kind, mutate=None):
    d = json.loads(run("rubdoc.py", "template", kind).stdout)
    if mutate:
        mutate(d)
    f = tmp_path / f"{kind}.json"
    f.write_text(json.dumps(d), encoding="utf-8")
    return f


@pytest.mark.parametrize("kind,out", [("case", "CASESTUDY.html"), ("learn", "LEARN-PLAN.html"), ("build", "BUILD-PLAN.html")])
def test_rubdoc_templates_check_and_render(tmp_path, kind, out):
    f = doc_json(tmp_path, kind)
    run("rubdoc.py", "check", kind, f)
    run("rubdoc.py", "render", kind, f)
    page = (tmp_path / out).read_text(encoding="utf-8")
    assert page.startswith("<!doctype html>") and "Sample." in page and "viewport" in page


def test_case_fact_without_source_is_an_error(tmp_path):
    def m(d):
        d["funding"]["total_raised"]["sources"] = []
    r = run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", m), ok=False)
    assert r.returncode == 1 and "total_raised" in r.stdout


def test_case_unknown_fact_needs_no_source_and_never_shows_a_guess(tmp_path):
    def m(d):
        d["funding"]["valuation"] = {"value": "$2 billion", "confidence": "unknown", "sources": []}
    f = doc_json(tmp_path, "case", m)
    run("rubdoc.py", "check", "case", f)
    run("rubdoc.py", "render", "case", f)
    page = (tmp_path / "CASESTUDY.html").read_text(encoding="utf-8")
    assert "$2 billion" not in page and "Not publicly confirmed" in page


def test_case_requires_drawbacks(tmp_path):
    def m(d):
        d["drawbacks"] = []
    r = run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", m), ok=False)
    assert "drawbacks" in r.stdout


def test_case_confirmed_tech_needs_evidence(tmp_path):
    def m(d):
        d["tech"][0]["confidence"] = "confirmed"
        d["tech"][0]["evidence"] = []
    assert run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", m), ok=False).returncode == 1


def test_case_rejects_non_http_sources_and_escapes_html(tmp_path):
    def m(d):
        d["snapshot"]["founded"]["sources"] = ["javascript:alert(1)"]
    assert run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", m), ok=False).returncode == 1

    def m2(d):
        d["name"] = "<img src=x onerror=alert(1)>"
    f = doc_json(tmp_path, "case", m2)
    run("rubdoc.py", "render", "case", f)
    assert "<img src=x" not in (tmp_path / "CASESTUDY.html").read_text(encoding="utf-8")


def test_learn_rejects_bad_resource_and_overloaded_week(tmp_path):
    def bad(d):
        d["weeks"][0]["topics"][0]["resources"][0]["url"] = "not a url"
    assert run("rubdoc.py", "check", "learn", doc_json(tmp_path, "learn", bad), ok=False).returncode == 1

    def heavy(d):
        d["hours_per_week"] = 3
    r = run("rubdoc.py", "check", "learn", doc_json(tmp_path, "learn", heavy))
    assert "WARN" in r.stdout and "3h/week" in r.stdout


def test_build_needs_real_prompts_acceptance_and_unique_ids(tmp_path):
    def short(d):
        d["phases"][0]["stages"][0]["prompt"] = "build it"
    assert run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", short), ok=False).returncode == 1

    def noacc(d):
        d["phases"][0]["stages"][1]["acceptance"] = []
    assert run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", noacc), ok=False).returncode == 1

    def dup(d):
        d["phases"][1]["stages"][0]["id"] = d["phases"][0]["stages"][0]["id"]
    assert run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", dup), ok=False).returncode == 1


def test_build_must_be_phased_mvp_first_one_feature_each(tmp_path):
    def single(d):
        d["phases"] = d["phases"][:1]
    r = run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", single), ok=False)
    assert r.returncode == 1 and "MVP plus at least one feature" in r.stdout

    def wrong_first(d):
        d["phases"][0]["kind"] = "feature"
    assert run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", wrong_first), ok=False).returncode == 1

    def no_why(d):
        del d["phases"][1]["why_next"]
    assert run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", no_why), ok=False).returncode == 1

    def no_exit(d):
        d["phases"][2]["exit_criteria"] = []
    assert "exit_criteria" in run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", no_exit), ok=False).stdout


def test_build_warns_when_mvp_or_feature_too_big(tmp_path):
    def big(d):
        for s in d["phases"][0]["stages"]:
            s["hours"] = 12
        for s in d["phases"][1]["stages"]:
            s["hours"] = 15
    r = run("rubdoc.py", "check", "build", doc_json(tmp_path, "build", big))
    assert "the MVP is" in r.stdout and "one feature is" in r.stdout


def test_build_export_writes_context_phase_briefs_and_stage_prompts(tmp_path):
    f = doc_json(tmp_path, "build")
    out = tmp_path / "prompts"
    run("rubdoc.py", "export", f, "--out", out)
    names = sorted(p.name for p in out.iterdir())
    assert names[0] == "00-project-context.md" and "PROMPTS.md" in names and len(names) == 14
    assert "p2-00-phase-brief.md" in names and "p1-01-project-skeleton-and-auth.md" in names
    ctx = (out / "00-project-context.md").read_text(encoding="utf-8")
    assert "do not copy" in ctx and "FastAPI" in ctx and "one phase at a time" in ctx
    brief = (out / "p2-00-phase-brief.md").read_text(encoding="utf-8")
    assert "add ONE feature" in brief and "PROGRESS.md" in brief
    assert "Create a Next.js app" in (out / "p1-01-project-skeleton-and-auth.md").read_text(encoding="utf-8")


def test_case_needs_competitors_with_angle_and_sources(tmp_path):
    def none(d):
        d["market"]["competitors"] = []
    r = run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", none), ok=False)
    assert r.returncode == 1 and "competitors" in r.stdout

    def bad_angle(d):
        d["market"]["competitors"][0]["angle"] = "vibes"
    assert run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", bad_angle), ok=False).returncode == 1

    def nosrc(d):
        d["market"]["competitors"][1]["sources"] = []
    assert run("rubdoc.py", "check", "case", doc_json(tmp_path, "case", nosrc), ok=False).returncode == 1


def test_case_renders_competitor_section_and_white_space(tmp_path):
    f = doc_json(tmp_path, "case")
    run("rubdoc.py", "render", "case", f)
    page = (tmp_path / "CASESTUDY.html").read_text(encoding="utf-8")
    assert "Competitors and how they differentiate" in page and "White space" in page and "BigCRM Assistant" in page


def test_dashboard_links_case_study(tmp_path):
    s = tmp_path / "studies" / "demo"
    run("ledger.py", "init", s, "--subject", "Demo", "--kind", "product")
    (s / "CASESTUDY.html").write_text("<html></html>")
    run("dashboard.py", tmp_path)
    assert "demo/CASESTUDY.html" in (tmp_path / "DASHBOARD.html").read_text(encoding="utf-8")
