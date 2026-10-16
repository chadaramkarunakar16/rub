#!/usr/bin/env python3
"""RUB walkthrough: screenshot public pages the way a visitor sees them.

This is the fallback when no interactive browser (Claude's built-in browser or Claude in Chrome) is
connected. It only loads pages and records what is visible: a screenshot and the page's visible text.
It does not log in, fill forms, click purchase buttons, or inspect network traffic or code.
It honours robots.txt and waits between pages.

Commands
  shoot   <out-dir> URL [URL ...] [--device desktop|mobile] [--full-page] [--delay SECONDS]
  gallery <out-dir>      rebuild GALLERY.md from every screenshot in <out-dir>/screens

Needs: pip install playwright   then   python -m playwright install chromium
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import time
import urllib.parse
import urllib.robotparser
from pathlib import Path

DEVICES = {
    "desktop": {"viewport": {"width": 1440, "height": 900}, "is_mobile": False},
    "mobile": {"viewport": {"width": 390, "height": 844}, "is_mobile": True, "device_scale_factor": 3,
               "has_touch": True},
}
TEXT_LIMIT = 20000


def slugify(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    s = (parts.netloc + parts.path).strip("/").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s or "page")[:60]


_robots: dict[str, urllib.robotparser.RobotFileParser | None] = {}


def allowed(url: str, agent: str = "*") -> bool:
    parts = urllib.parse.urlsplit(url)
    base = f"{parts.scheme}://{parts.netloc}"
    if base not in _robots:
        rp = urllib.robotparser.RobotFileParser(base + "/robots.txt")
        try:
            rp.read()
            _robots[base] = rp
        except Exception:
            _robots[base] = None  # robots.txt unreachable: treat as allowed
    rp = _robots[base]
    return True if rp is None else rp.can_fetch(agent, url)


def next_index(screens: Path) -> int:
    nums = [int(m.group(1)) for p in screens.glob("*.png") if (m := re.match(r"(\d+)-", p.name))]
    return (max(nums) if nums else 0) + 1


def cmd_shoot(a) -> int:
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        sys.exit("error: Playwright is not installed. Run: pip install playwright  then  "
                 "python -m playwright install chromium")
    out = Path(a.out)
    screens = out / "screens"
    screens.mkdir(parents=True, exist_ok=True)
    log_path = out / "shots.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    idx = next_index(screens)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(**DEVICES[a.device])
        page = ctx.new_page()
        for n, url in enumerate(a.urls):
            if not url.startswith(("http://", "https://")):
                print(f"skip {url}: not an http(s) URL")
                continue
            if not allowed(url):
                print(f"skip {url}: disallowed by robots.txt")
                log.append({"url": url, "status": "skipped-robots", "at": dt.datetime.now().isoformat()})
                continue
            if n:
                time.sleep(a.delay)
            name = f"{idx:02d}-{slugify(url)}-{a.device}"
            entry = {"url": url, "device": a.device, "at": dt.datetime.now().isoformat(timespec="seconds")}
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except PWTimeout:
                    pass  # busy pages never go idle; the content is loaded
                page.screenshot(path=str(screens / f"{name}.png"), full_page=a.full_page)
                text = page.evaluate("() => document.body ? document.body.innerText : ''") or ""
                (screens / f"{name}.txt").write_text(
                    f"URL: {page.url}\nTitle: {page.title()}\n\n{text[:TEXT_LIMIT]}", encoding="utf-8")
                entry.update(status="ok", http_status=resp.status if resp else None, final_url=page.url,
                             title=page.title(), screenshot=f"screens/{name}.png", text=f"screens/{name}.txt")
                print(f"ok   {url} -> screens/{name}.png")
                idx += 1
            except Exception as exc:  # report and keep going
                entry.update(status="error", error=str(exc).splitlines()[0])
                print(f"fail {url}: {entry['error']}")
            log.append(entry)
        browser.close()
    log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")
    write_gallery(out)
    return 0


def write_gallery(out: Path) -> None:
    screens = out / "screens"
    shots = {}
    log_path = out / "shots.json"
    if log_path.exists():
        for e in json.loads(log_path.read_text(encoding="utf-8")):
            if e.get("screenshot"):
                shots[e["screenshot"]] = e
    lines = ["# Walkthrough screenshots", "", f"Updated {dt.date.today().isoformat()}.", ""]
    for png in sorted(screens.glob("*.png")):
        rel = f"screens/{png.name}"
        e = shots.get(rel, {})
        title = e.get("title") or png.stem
        lines += [f"## {png.stem}", ""]
        if e.get("url"):
            lines.append(f"{title} · <{e['url']}> · {e.get('device', '')} · {e.get('at', '')}")
            lines.append("")
        lines += [f"![{png.stem}]({rel})", ""]
    (out / "GALLERY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out / 'GALLERY.md'}")


def cmd_gallery(a) -> int:
    out = Path(a.out)
    if not (out / "screens").is_dir():
        sys.exit(f"error: {out / 'screens'} does not exist")
    write_gallery(out)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Screenshot public pages as a visitor sees them")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("shoot"); s.add_argument("out"); s.add_argument("urls", nargs="+")
    s.add_argument("--device", choices=DEVICES, default="desktop")
    s.add_argument("--full-page", action="store_true")
    s.add_argument("--delay", type=float, default=3.0, help="seconds between pages (default 3)")
    s.set_defaults(fn=cmd_shoot)
    s = sub.add_parser("gallery"); s.add_argument("out"); s.set_defaults(fn=cmd_gallery)
    a = p.parse_args(argv)
    if getattr(a, "delay", 3.0) < 1:
        sys.exit("error: --delay must be at least 1 second")
    return a.fn(a) or 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
