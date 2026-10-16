#!/usr/bin/env python3
"""doctor.py - check that RUB is installed correctly and ready to use.

Usage:
  python doctor.py [--plugin-root DIR] [--offline]

Checks the plugin files (manifest, skills, agents, scripts, references), then your machine
(Python, git, Claude CLI, Playwright browser for the observe fallback, internet access).
Exit code is 1 if any required check fails.
"""
import argparse, json, os, re, shutil, subprocess, sys, urllib.request
from pathlib import Path

OK, WARN, BAD = "ok  ", "warn", "FAIL"


def frontmatter(path):
    text = path.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


def plugin_checks(root: Path, res):
    def add(status, msg):
        res.append((status, msg))

    pj = root / ".claude-plugin" / "plugin.json"
    try:
        meta = json.loads(pj.read_text(encoding="utf-8"))
        add(OK, f"plugin.json: {meta.get('name')} v{meta.get('version')}")
    except Exception as e:
        add(BAD, f"plugin.json missing or invalid ({e})")
    mj = root / ".claude-plugin" / "marketplace.json"
    add(OK if mj.exists() else WARN, "marketplace.json " + ("found" if mj.exists() else "missing (needed only to install from a folder)"))

    skills = sorted((root / "skills").glob("*/SKILL.md"))
    bad = [p.parent.name for p in skills if not (frontmatter(p) or {}).get("description")]
    add(OK if skills and not bad else BAD, f"{len(skills)} skills" + (f"; missing description: {', '.join(bad)}" if bad else ""))
    agents = sorted((root / "agents").glob("*.md"))
    bad = [p.stem for p in agents if not {"name", "description"} <= set(frontmatter(p) or {})]
    add(OK if agents and not bad else BAD, f"{len(agents)} agents" + (f"; bad frontmatter: {', '.join(bad)}" if bad else ""))

    # every script / reference mentioned in a skill or agent must exist
    missing = set()
    for p in list(skills) + list(agents):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in re.finditer(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+?\.(?:py|md))", text):
            if not (root / m.group(1)).exists():
                missing.add(f"{m.group(1)} (in {p.relative_to(root)})")
    add(OK if not missing else BAD, "all referenced scripts and guides exist" if not missing else "missing: " + "; ".join(sorted(missing)))

    # every agent named in a skill must exist
    names = {(frontmatter(p) or {}).get("name") for p in agents}
    unknown = set()
    for p in skills:
        for m in re.finditer(r"rub:([a-z-]+)", p.read_text(encoding="utf-8", errors="ignore")):
            n = m.group(1)
            if n not in names and not (root / "skills" / n).exists():
                unknown.add(n)
    add(OK if not unknown else BAD, "all agents and commands named in workflows exist" if not unknown else "unknown names: " + ", ".join(sorted(unknown)))

    for s in sorted((root / "scripts").glob("*.py")):
        r = subprocess.run([sys.executable, "-m", "py_compile", str(s)], capture_output=True, text=True)
        if r.returncode:
            add(BAD, f"{s.name} does not compile: {r.stderr.strip()[:120]}")
    add(OK, "all scripts compile")
    add(OK if (root / "LICENSE").exists() else WARN, "LICENSE " + ("found" if (root / "LICENSE").exists() else "missing"))


def machine_checks(res, offline):
    v = sys.version_info
    res.append((OK if v >= (3, 9) else BAD, f"Python {v.major}.{v.minor}.{v.micro} (needs 3.9+)"))
    for tool, need, hint in (("git", False, "needed to clone repos for /opensource"),
                             ("claude", False, "Claude Code CLI; only needed for the headless tests")):
        p = shutil.which(tool)
        res.append((OK if p else WARN, f"{tool}: {p or 'not found'}" + ("" if p else f" ({hint})")))
    try:
        import playwright  # noqa: F401
        res.append((OK, "playwright (python) installed: screenshots work without a browser tool"))
    except ImportError:
        res.append((WARN, "playwright not installed: /observe uses the built-in browser or Chrome instead. "
                          "To enable the fallback: pip install playwright && python -m playwright install chromium"))
    if not offline:
        try:
            urllib.request.urlopen(urllib.request.Request("https://example.com", headers={"User-Agent": "doctor"}), timeout=6)
            res.append((OK, "internet reachable"))
        except Exception as e:
            res.append((WARN, f"internet check failed ({type(e).__name__}): research commands need web access"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plugin-root", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--offline", action="store_true")
    a = ap.parse_args(argv)
    res = []
    plugin_checks(Path(a.plugin_root), res)
    machine_checks(res, a.offline)
    for s, m in res:
        print(f"[{s}] {m}")
    fails = sum(1 for s, _ in res if s == BAD)
    warns = sum(1 for s, _ in res if s == WARN)
    print(f"\n{fails} failed, {warns} warnings" + (" - fix the FAIL lines first." if fails else " - ready."))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
