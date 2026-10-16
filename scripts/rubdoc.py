#!/usr/bin/env python3
"""rubdoc.py - the three documents RUB produces, as self-contained HTML.

  case   -> CASESTUDY.html    what the startup is, how it got funded, why it leads, its tech, its drawbacks
  learn  -> LEARN-PLAN.html   what you must learn to build it yourself by hand, week by week
  build  -> BUILD-PLAN.html   stack, architecture, data model and step-by-step vibe-coding prompts

Commands
  template case|learn|build           print an example JSON (a fictional sample company)
  check    case|learn|build FILE      validate; exit 1 on errors
  render   case|learn|build FILE      write the HTML next to FILE (or --out)
  export   FILE.json --out DIR        build plan -> prompts/00-project-context.md, 01-....md, PROMPTS.md

Rules the checker enforces: every factual claim carries a confidence label and, unless it is
"unknown", at least one http(s) source. Unknown facts are shown as "Not publicly confirmed"
instead of being guessed. A case study must list drawbacks.

Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

CONF = ("confirmed", "reported", "estimate", "unknown")
CONF_LABEL = {"confirmed": "Confirmed", "reported": "Reported", "estimate": "Estimate", "unknown": "Not public"}
TECH_CONF = ("confirmed", "typical")
ANGLES = ("price", "niche", "speed", "quality", "integrations", "region", "brand", "openness", "distribution", "other")
KINDS = ("docs", "video", "course", "book", "tutorial", "article")


def esc(x) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def is_url(u) -> bool:
    try:
        p = urlparse(str(u))
        return p.scheme in ("http", "https") and bool(p.netloc)
    except ValueError:
        return False


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "item"


# ---------------------------------------------------------------- templates (fictional sample)

CASE_TEMPLATE = {
    "name": "Sampleo",
    "sample": True,
    "tagline": "FICTIONAL SAMPLE: AI notes for field sales teams",
    "website": "https://example.com",
    "as_of": "2026-10-16",
    "snapshot": {
        "founded": {"value": "2024", "confidence": "confirmed", "sources": ["https://example.com/about"]},
        "founders": {"value": "Asha Rao (CEO), Daniel Kim (CTO)", "confidence": "confirmed", "sources": ["https://example.com/about"]},
        "headquarters": {"value": "Bengaluru, India", "confidence": "confirmed", "sources": ["https://example.com/about"]},
        "category": {"value": "Sales productivity / voice AI", "confidence": "confirmed", "sources": ["https://example.com"]},
        "team_size": {"value": "About 25", "confidence": "reported", "sources": ["https://example.com/news/team"]},
        "stage": {"value": "Seed", "confidence": "confirmed", "sources": ["https://example.com/news/seed"]}
    },
    "funding": {
        "total_raised": {"value": "$6.5M", "confidence": "reported", "sources": ["https://example.com/news/seed"]},
        "valuation": {"value": "Not publicly confirmed", "confidence": "unknown", "sources": []},
        "latest_round": {"value": "Seed, Mar 2026", "confidence": "confirmed", "sources": ["https://example.com/news/seed"]},
        "rounds": [
            {"round": "Seed", "date": "2026-03", "amount": "$6.5M", "lead_investors": "Example Ventures",
             "other_investors": "Angel investors from sales-tech", "sources": ["https://example.com/news/seed"]}
        ],
        "why_funded": [
            {"point": "A painful, daily problem for a clear buyer: reps lose hours typing notes after visits",
             "sources": ["https://example.com/news/seed"]},
            {"point": "Fast early traction: 400 paying teams within 9 months of launch",
             "sources": ["https://example.com/news/seed"]}
        ]
    },
    "problem": "Field sales reps spend about an hour a day writing up visits, so CRMs stay stale and managers fly blind.",
    "solution": "Reps talk after a visit; the app turns the voice note into a structured CRM update and next-step reminders.",
    "who_its_for": "Sales teams of 10-200 reps who visit customers in person (pharma, FMCG, building materials).",
    "features": [
        {"name": "Voice-to-CRM update", "what": "Speak for 30 seconds; get a filled CRM record.",
         "why_it_matters": "Removes the task reps hate most, so adoption is high.",
         "how_it_works": "Speech-to-text, then an LLM extracts fields into a fixed schema, then a CRM API write.",
         "sources": ["https://example.com/product"]},
        {"name": "Manager digest", "what": "A daily summary of every visit.",
         "why_it_matters": "Gives the buyer (the manager) a reason to pay.",
         "how_it_works": "Scheduled job summarises the day's structured records.", "sources": ["https://example.com/product"]}
    ],
    "usp": [
        {"point": "Works offline in poor-signal areas", "detail": "Records on device and syncs later, which general note apps do not do."},
        {"point": "Regional-language voice", "detail": "Supports 8 Indian languages with mixed-language speech."}
    ],
    "business_model": {
        "revenue": "Per-seat subscription, sold to the sales manager.",
        "value_metric": "Active rep per month",
        "pricing": [
            {"plan": "Team", "price": "$18 / rep / month", "notes": "Billed annually"},
            {"plan": "Enterprise", "price": "Custom", "notes": "SSO, audit logs, CRM custom fields"}
        ],
        "unit_economics_note": "Not public. Gross margin depends on speech and LLM cost per minute; see the build plan for cost control."
    },
    "market": {
        "position": {"value": "Challenger in a growing niche, behind the large CRM vendors' built-in assistants", "confidence": "estimate",
                     "sources": ["https://example.com/market-report"]},
        "why_leading": ["Owns the offline, regional-language niche that big vendors ignore",
                        "Bottom-up adoption by reps, then a manager-led upgrade"],
        "differentiation_summary": "Sampleo competes on offline use and regional languages; the big CRMs compete on distribution and bundling, and note apps compete on price.",
        "competitors": [
            {"name": "BigCRM Assistant", "website": "https://example.com/bigcrm", "angle": "distribution",
             "what_they_do": "AI assistant built into the largest CRM.",
             "how_they_differentiate": "Already installed for every customer of the CRM, so adoption costs nothing.",
             "pricing": "Bundled in the CRM's top plan", "traction": "Offered to millions of CRM seats (company statement)",
             "strengths": ["Zero setup", "Data already in the CRM"], "weaknesses": ["Needs a connection", "Few languages"],
             "sources": ["https://example.com/bigcrm/assistant"]},
            {"name": "GenericNotes", "website": "https://example.com/genericnotes", "angle": "price",
             "what_they_do": "General voice-notes app.",
             "how_they_differentiate": "Cheap and simple for any profession.",
             "pricing": "$4 / user / month", "traction": "Not publicly confirmed",
             "strengths": ["Low price", "Easy to try"], "weaknesses": ["Free-text output, not CRM fields"],
             "sources": ["https://example.com/genericnotes/pricing"]},
            {"name": "VoiceForms", "website": "https://example.com/voiceforms", "angle": "speed",
             "what_they_do": "Fills forms and CRM fields from speech for any industry.",
             "how_they_differentiate": "Fastest capture: results appear while the rep is still talking.",
             "pricing": "$25 / user / month", "traction": "Seed round reported last quarter",
             "strengths": ["Real-time results", "Polished mobile app"], "weaknesses": ["English only", "No offline mode"],
             "sources": ["https://example.com/voiceforms/news"]}
        ],
        "white_space": [
            {"gap": "Offline-first capture for rural field teams", "evidence": "Neither competitor supports it (their docs require a connection)"}
        ],
        "traction": [{"point": "400 paying teams", "sources": ["https://example.com/news/seed"]}]
    },
    "growth": [
        {"tactic": "Founder-led demos to 50 sales managers", "detail": "The first 50 customers came from personal outreach.",
         "sources": ["https://example.com/blog/first-50"]},
        {"tactic": "Short demo videos on LinkedIn", "detail": "Rep-in-the-field clips showing the 30-second flow.",
         "sources": ["https://example.com/linkedin"]}
    ],
    "strengths": ["Clear buyer and clear pain", "High rep adoption because it removes a chore", "Local-language moat"],
    "drawbacks": [
        {"point": "Depends on third-party speech and LLM prices", "detail": "A price rise or quality drop hits margin directly."},
        {"point": "Large CRMs can copy the core feature", "detail": "Distribution advantage favours incumbents if they prioritise it."}
    ],
    "tech": [
        {"layer": "Mobile app", "choice": "React Native with local storage for offline", "confidence": "typical",
         "evidence": [], "note": "Typical approach for offline-first field apps"},
        {"layer": "Backend", "choice": "Python API on managed cloud", "confidence": "confirmed",
         "evidence": ["https://example.com/careers/backend-engineer"], "note": "From a public job post"},
        {"layer": "AI", "choice": "Speech-to-text + LLM structured extraction", "confidence": "typical",
         "evidence": [], "note": "Standard pipeline for voice-to-form products"}
    ],
    "timeline": [
        {"date": "2024", "event": "Founded", "sources": ["https://example.com/about"]},
        {"date": "2025-06", "event": "Public launch", "sources": ["https://example.com/blog/launch"]},
        {"date": "2026-03", "event": "Seed round announced", "sources": ["https://example.com/news/seed"]}
    ],
    "opportunities": [
        {"gap": "Field teams in other trades (insurance agents, clinic reps)", "how_to_win": "Same pipeline, different schema and language packs"}
    ]
}

LEARN_TEMPLATE = {
    "product": "Sampleo",
    "sample": True,
    "goal": "Build a voice-to-CRM mobile app by hand, without AI writing the code",
    "level": "some-coding",
    "hours_per_week": 10,
    "concepts": [{"term": "Structured extraction", "plain": "Asking a language model to return data in a fixed shape (like a form) instead of free text."}],
    "weeks": [
        {"week": 1, "theme": "Web and API basics", "milestone": "A small API that stores and returns notes",
         "topics": [
             {"topic": "HTTP and REST", "why": "Your app and server talk this way.", "hours": 4, "exercise": "Build a notes API with create and list endpoints.",
              "resources": [{"title": "MDN: An overview of HTTP", "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview", "kind": "docs"}]},
             {"topic": "SQL and a database", "why": "Visits and notes need durable storage.", "hours": 5, "exercise": "Create tables for users, visits and notes; write 5 queries.",
              "resources": [{"title": "SQLite tutorial", "url": "https://www.sqlite.org/lang.html", "kind": "docs"}]}
         ]},
        {"week": 2, "theme": "Voice and AI extraction", "milestone": "Audio in, structured record out",
         "topics": [
             {"topic": "Calling a speech-to-text API", "why": "Turns the rep's voice into text.", "hours": 4, "exercise": "Transcribe three recordings and compare accuracy.",
              "resources": [{"title": "Provider docs of your choice", "url": "https://example.com/stt-docs", "kind": "docs"}]},
             {"topic": "Prompting for JSON output", "why": "Converts text into CRM fields reliably.", "hours": 5, "exercise": "Extract 6 fields from 20 sample transcripts and measure errors.",
              "resources": [{"title": "Structured output guide", "url": "https://example.com/structured-output", "kind": "article"}]}
         ]}
    ],
    "skip_for_now": ["Kubernetes", "Microservices", "Custom speech models"]
}

BUILD_TEMPLATE = {
    "product": "Sampleo",
    "sample": True,
    "summary": "A mobile-first app where a field rep records a voice note after a visit and it becomes a structured CRM record.",
    "scope": {"in": ["Record voice note", "Transcribe", "Extract fields", "Show, edit and confirm the record"],
              "out": ["Manager daily digest (phase 2)", "Offline capture (phase 3)", "Real CRM integrations (use CSV export first)", "Team admin"]},
    "stack": {
        "frontend": {"choice": "Next.js (responsive web app / PWA)", "why": "One codebase, easy to deploy, works on phones", "alternatives": "React Native, Flutter"},
        "backend": {"choice": "FastAPI (Python)", "why": "Quick to write, good for AI calls", "alternatives": "Node + Express"},
        "database": {"choice": "PostgreSQL (Supabase)", "why": "Relational data, free tier", "alternatives": "SQLite, Firebase"},
        "auth": {"choice": "Supabase Auth", "why": "Email login in an hour", "alternatives": "Clerk, Auth.js"},
        "ai": {"choice": "Speech-to-text API + LLM with JSON output", "why": "No model hosting needed", "alternatives": "Open-source Whisper"},
        "hosting": {"choice": "Vercel + Render", "why": "Free tiers", "alternatives": "Fly.io"}
    },
    "architecture": {
        "components": [{"name": "Web app", "role": "Recording UI, record list, edit screen"},
                       {"name": "API", "role": "Auth, upload, orchestration, storage"},
                       {"name": "AI worker", "role": "Transcribe and extract fields"}],
        "flows": [{"name": "Voice note to record",
                   "steps": ["Rep taps record and speaks", "App uploads audio to API", "API stores audio and queues a job",
                             "Worker transcribes the audio", "Worker extracts fields as JSON", "API saves the record", "App shows the record for review"]}]
    },
    "data_model": [
        {"entity": "users", "fields": ["id", "email", "team_id"], "notes": "From auth"},
        {"entity": "visits", "fields": ["id", "user_id", "customer_name", "audio_url", "transcript", "created_at"], "notes": ""},
        {"entity": "records", "fields": ["id", "visit_id", "fields_json", "status"], "notes": "status: draft or confirmed"}
    ],
    "api": [{"method": "POST", "path": "/visits", "purpose": "Upload audio and create a visit"},
            {"method": "GET", "path": "/visits", "purpose": "List my visits"},
            {"method": "PATCH", "path": "/records/{id}", "purpose": "Edit and confirm a record"}],
    "phases": [
        {"id": "p1", "kind": "mvp", "name": "Voice note to a confirmed record",
         "goal": "One rep can record a visit, get a structured record, fix it and confirm it",
         "user_value": "Saves the rep about an hour a day of typing",
         "exit_criteria": ["5 real reps use it on real visits for a week", "At least 8 of 10 records need one edit or fewer",
                           "Capture takes under 2 minutes end to end", "Cost per visit is logged and within your budget"],
         "stages": [
             {"id": "p1s1", "name": "Project skeleton and auth", "goal": "Running app with login", "hours": 4,
              "deliverable": "Login page and an empty dashboard, deployed",
              "prompt": "Create a Next.js app with Supabase email authentication. Add a protected /dashboard page that shows the signed-in user's email. Use TypeScript and a clean, mobile-first layout. Explain each file you create in one line. Stop when the acceptance checks pass.",
              "acceptance": ["I can sign up, sign in and sign out", "Dashboard is unreachable when signed out"], "learn_first": ["HTTP and REST"]},
             {"id": "p1s2", "name": "Database and visits API", "goal": "Create and list visits", "hours": 5,
              "deliverable": "visits table and two endpoints",
              "prompt": "Add the visits and records tables from the data model using migrations. Build POST /visits and GET /visits in FastAPI, checking the signed-in user. Add tests for both endpoints. Stop when the acceptance checks pass.",
              "acceptance": ["A visit created by user A is not visible to user B", "Tests pass"], "learn_first": ["SQL and a database"]},
             {"id": "p1s3", "name": "Record and upload audio", "goal": "Record in the browser and upload", "hours": 5,
              "deliverable": "Record button, upload progress, saved audio",
              "prompt": "Add a record screen that captures microphone audio with the MediaRecorder API, shows a timer, and uploads the file to POST /visits. Handle denied microphone permission with a clear message. Stop when the acceptance checks pass.",
              "acceptance": ["Audio plays back from storage", "Permission denied shows a helpful message"], "learn_first": []},
             {"id": "p1s4", "name": "Transcribe and extract", "goal": "Turn audio into structured fields", "hours": 6,
              "deliverable": "Worker that fills records.fields_json",
              "prompt": "Add a background job that transcribes a visit's audio with a speech-to-text API and then calls an LLM to extract customer, outcome, next step and follow-up date as JSON matching a fixed schema. Validate the JSON and retry once on failure. Log the cost per visit. Stop when the acceptance checks pass.",
              "acceptance": ["20 sample recordings produce valid JSON at least 90% of the time", "Failures are visible in the UI"],
              "learn_first": ["Calling a speech-to-text API", "Prompting for JSON output"]},
             {"id": "p1s5", "name": "Review and confirm", "goal": "Let the rep fix and approve a record", "hours": 4,
              "deliverable": "Edit screen with a Confirm button",
              "prompt": "Build a review screen that shows the extracted fields with inline editing and a Confirm button that sets the record status to confirmed. Confirmed records must not change silently. Keep the UI minimal. Stop when the acceptance checks pass.",
              "acceptance": ["Confirmed records are locked until the rep re-opens them", "Edits are saved and shown after a refresh"], "learn_first": []}
         ]},
        {"id": "p2", "kind": "feature", "name": "Manager daily digest", "feature": "Manager daily digest",
         "goal": "A manager gets one summary of yesterday's confirmed visits",
         "why_next": "The manager is the buyer, and the digest gives them a reason to pay; the cheap note apps in the case study do not offer it",
         "user_value": "Managers see the field without chasing reps",
         "exit_criteria": ["3 managers open the digest 3 days in a row", "Digest generation cost per team is under your budget"],
         "stages": [
             {"id": "p2s1", "name": "Teams and roles", "goal": "Group reps under a manager", "hours": 3,
              "deliverable": "teams table, manager role and an invite step",
              "prompt": "Add a teams table and a manager role to the existing app. A manager can see confirmed records of reps on their team and nobody else's. Do not change the rep screens. Add tests for the permission rule. Stop when the acceptance checks pass.",
              "acceptance": ["A manager sees only their team's confirmed records", "Reps still see only their own visits"], "learn_first": []},
             {"id": "p2s2", "name": "Digest job and email", "goal": "Send the daily summary", "hours": 4,
              "deliverable": "Scheduled job that emails a summary per team",
              "prompt": "Add a scheduled job that, each morning, summarises yesterday's confirmed records for each team (counts, outcomes, follow-ups due) and emails it to the manager. Keep the summary template in one file. Add an unsubscribe link. Stop when the acceptance checks pass.",
              "acceptance": ["Digest lists yesterday's confirmed visits", "Unsubscribe works"], "learn_first": []}
         ]},
        {"id": "p3", "kind": "feature", "name": "Offline capture", "feature": "Offline capture",
         "goal": "A rep can record with no signal and have it upload later",
         "why_next": "White space in the case study: neither of the main competitors works offline, and field reps often have poor signal",
         "user_value": "Reps in poor-signal areas can use the product at all",
         "exit_criteria": ["A recording made in airplane mode uploads after reconnecting with nothing lost", "3 reps in poor-signal areas use it for a week"],
         "stages": [
             {"id": "p3s1", "name": "Local queue", "goal": "Store recordings on the device when offline", "hours": 5,
              "deliverable": "Service worker and a local queue of pending recordings",
              "prompt": "Make the web app installable (PWA) and add a service worker. When the upload fails because the device is offline, store the recording in IndexedDB and show it as 'waiting to upload'. Do not change the online flow. Stop when the acceptance checks pass.",
              "acceptance": ["An offline recording appears as waiting", "The online flow still works"], "learn_first": []},
             {"id": "p3s2", "name": "Sync and retries", "goal": "Upload the queue when back online", "hours": 5,
              "deliverable": "Automatic sync with retry and no duplicates",
              "prompt": "When the connection returns, upload queued recordings one at a time with retry and exponential backoff. Use a client-generated id so a retried upload never creates a duplicate visit. Show sync status per recording. Add tests for the duplicate rule. Stop when the acceptance checks pass.",
              "acceptance": ["Interrupting a sync and retrying creates no duplicate visits", "Status shows waiting, uploading, done or failed"], "learn_first": []}
         ]}
    ],
    "launch_checklist": ["Privacy note explaining audio storage and deletion", "Rate limits on uploads", "Error monitoring", "5 real users testing for a week"],
    "risks": ["Speech accuracy on accents and noise", "LLM cost per recording", "Storing voice data needs consent and a deletion option"]
}

TEMPLATES = {"case": CASE_TEMPLATE, "learn": LEARN_TEMPLATE, "build": BUILD_TEMPLATE}

# ---------------------------------------------------------------- validation


def _need_str(d, key, path, errs):
    if not isinstance(d.get(key), str) or not d[key].strip():
        errs.append(f"{path}.{key} is required")


def _check_sources(srcs, path, errs):
    if not isinstance(srcs, list) or not srcs:
        errs.append(f"{path}: needs at least one source URL")
        return
    for s in srcs:
        if not is_url(s):
            errs.append(f"{path}: source is not an http(s) URL: {s!r}")


def _check_fact(f, path, errs):
    if not isinstance(f, dict):
        errs.append(f"{path} must be an object with value, confidence, sources")
        return
    _need_str(f, "value", path, errs)
    c = f.get("confidence")
    if c not in CONF:
        errs.append(f"{path}.confidence must be one of {', '.join(CONF)}")
    elif c != "unknown":
        _check_sources(f.get("sources"), path, errs)


def problems(kind: str, d: dict) -> tuple[list[str], list[str]]:
    errs: list[str] = []
    warns: list[str] = []
    if not isinstance(d, dict):
        return ["top level must be a JSON object"], []
    if kind == "case":
        for k in ("name", "tagline", "problem", "solution"):
            _need_str(d, k, "case", errs)
        for grp, keys in (("snapshot", ("founded", "founders", "headquarters", "category", "stage")),
                          ("funding", ("total_raised", "valuation", "latest_round"))):
            g = d.get(grp) or {}
            for k in keys:
                if k not in g:
                    errs.append(f"{grp}.{k} missing (use confidence \"unknown\" if not public)")
                else:
                    _check_fact(g[k], f"{grp}.{k}", errs)
            for k, v in g.items():
                if k not in keys and isinstance(v, dict):
                    _check_fact(v, f"{grp}.{k}", errs)
        for i, r in enumerate((d.get("funding") or {}).get("rounds", [])):
            for k in ("round", "date", "amount"):
                _need_str(r, k, f"funding.rounds[{i}]", errs)
            _check_sources(r.get("sources"), f"funding.rounds[{i}]", errs)
        for i, w in enumerate((d.get("funding") or {}).get("why_funded", [])):
            _need_str(w, "point", f"funding.why_funded[{i}]", errs)
            _check_sources(w.get("sources"), f"funding.why_funded[{i}]", errs)
        if not d.get("features"):
            errs.append("features: add at least one")
        for i, f in enumerate(d.get("features", [])):
            for k in ("name", "what", "why_it_matters"):
                _need_str(f, k, f"features[{i}]", errs)
            _check_sources(f.get("sources"), f"features[{i}]", errs)
        if not d.get("usp"):
            errs.append("usp: add at least one unique selling point")
        if not d.get("strengths"):
            errs.append("strengths: add at least one")
        if not d.get("drawbacks"):
            errs.append("drawbacks: a case study without drawbacks is a brochure; add at least one")
        elif len(d["drawbacks"]) < 2:
            warns.append("drawbacks: only one listed; look for a second (cost, dependence, competition, regulation)")
        bm = d.get("business_model") or {}
        if not bm.get("pricing"):
            warns.append("business_model.pricing is empty")
        m = d.get("market") or {}
        if "position" in m:
            _check_fact(m["position"], "market.position", errs)
        else:
            errs.append("market.position missing")
        comps = m.get("competitors") or []
        if not comps:
            errs.append("market.competitors: add the competitors that are doing well and how each differentiates")
        elif len(comps) < 3:
            warns.append("market.competitors: only %d listed; look for 3-5 (direct, indirect and the incumbent)" % len(comps))
        for i, c in enumerate(comps):
            p = f"market.competitors[{i}]"
            for k in ("name", "what_they_do", "how_they_differentiate"):
                _need_str(c, k, p, errs)
            if c.get("angle") not in ANGLES:
                errs.append(f"{p}.angle must be one of {', '.join(ANGLES)}")
            _check_sources(c.get("sources"), p, errs)
            if not c.get("weaknesses"):
                warns.append(f"{p} has no weaknesses listed; every competitor has some")
        if comps and not m.get("differentiation_summary"):
            warns.append("market.differentiation_summary is empty; say how the subject differs from these competitors")
        if not m.get("white_space"):
            warns.append("market.white_space is empty; what is nobody serving well?")
        for i, w in enumerate(m.get("white_space") or []):
            _need_str(w, "gap", f"market.white_space[{i}]", errs)
        for i, t in enumerate(d.get("tech", [])):
            if t.get("confidence") not in TECH_CONF:
                errs.append(f"tech[{i}].confidence must be confirmed or typical")
            elif t["confidence"] == "confirmed":
                _check_sources(t.get("evidence"), f"tech[{i}] (confirmed)", errs)
        if not d.get("tech"):
            warns.append("tech is empty; the Understand step needs it")
        for i, g in enumerate(d.get("growth", [])):
            _check_sources(g.get("sources"), f"growth[{i}]", errs)
        for i, t in enumerate(d.get("timeline", [])):
            _check_sources(t.get("sources"), f"timeline[{i}]", errs)
        if not d.get("growth"):
            warns.append("growth is empty; how they got users is a key lesson")
        if not d.get("opportunities"):
            warns.append("opportunities is empty")
    elif kind == "learn":
        for k in ("product", "goal"):
            _need_str(d, k, "learn", errs)
        if d.get("level") not in ("beginner", "some-coding", "developer"):
            errs.append("level must be beginner, some-coding or developer")
        hpw = d.get("hours_per_week")
        if not isinstance(hpw, (int, float)) or hpw <= 0:
            errs.append("hours_per_week must be a positive number")
            hpw = 10
        if not d.get("weeks"):
            errs.append("weeks: add at least one")
        for wi, w in enumerate(d.get("weeks", [])):
            tot = 0.0
            if not w.get("topics"):
                errs.append(f"weeks[{wi}] has no topics")
            for ti, t in enumerate(w.get("topics", [])):
                p = f"weeks[{wi}].topics[{ti}]"
                for k in ("topic", "why", "exercise"):
                    _need_str(t, k, p, errs)
                h = t.get("hours")
                if not isinstance(h, (int, float)) or h <= 0:
                    errs.append(f"{p}.hours must be positive")
                else:
                    tot += h
                if not t.get("resources"):
                    warns.append(f"{p} has no resources")
                for r in t.get("resources", []):
                    if not is_url(r.get("url")):
                        errs.append(f"{p}: resource URL invalid: {r.get('url')!r}")
                    if r.get("kind") not in KINDS:
                        errs.append(f"{p}: resource kind must be one of {', '.join(KINDS)}")
            if tot > hpw * 1.25:
                warns.append(f"week {w.get('week', wi + 1)} asks {tot:g}h but you have {hpw:g}h/week")
    elif kind == "build":
        for k in ("product", "summary"):
            _need_str(d, k, "build", errs)
        st = d.get("stack") or {}
        for k in ("frontend", "backend", "database"):
            if k not in st:
                errs.append(f"stack.{k} is required")
        for k, v in st.items():
            if not isinstance(v, dict) or not v.get("choice") or not v.get("why"):
                errs.append(f"stack.{k} needs choice and why")
        phases = d.get("phases") or []
        if len(phases) < 2:
            errs.append("phases: plan the MVP plus at least one feature phase after it (build step by step, not everything at once)")
        elif len(phases) < 3:
            warns.append("phases: only the MVP and one feature; plan the next 1-2 features too so the roadmap is visible")
        seen = set()
        for pi, ph in enumerate(phases):
            pp = f"phases[{pi}]"
            for k in ("id", "name", "goal"):
                _need_str(ph, k, pp, errs)
            want = "mvp" if pi == 0 else "feature"
            if ph.get("kind") != want:
                errs.append(f"{pp}.kind must be '{want}'" + (" (the first phase is always the MVP)" if pi == 0 else " (each later phase adds one feature)"))
            if pi > 0:
                _need_str(ph, "feature", pp, errs)
                _need_str(ph, "why_next", pp, errs)
            if not ph.get("exit_criteria"):
                errs.append(f"{pp}.exit_criteria: how will you know this phase worked before you move on?")
            stages = ph.get("stages") or []
            if not stages:
                errs.append(f"{pp}.stages: add at least one stage")
            hours = 0.0
            for si, s in enumerate(stages):
                p = f"{pp}.stages[{si}]"
                for k in ("id", "name", "goal", "deliverable"):
                    _need_str(s, k, p, errs)
                if s.get("id") in seen:
                    errs.append(f"{p}.id duplicated: {s.get('id')}")
                seen.add(s.get("id"))
                if not isinstance(s.get("prompt"), str) or len(s["prompt"].strip()) < 40:
                    errs.append(f"{p}.prompt must be a real prompt (40+ characters)")
                if not s.get("acceptance"):
                    errs.append(f"{p}.acceptance: how will you know it works?")
                if not isinstance(s.get("hours"), (int, float)) or s["hours"] <= 0:
                    errs.append(f"{p}.hours must be positive")
                else:
                    hours += s["hours"]
            if pi == 0 and hours > 40:
                warns.append(f"{pp}: the MVP is {hours:g} hours; cut scope until it fits in about 40")
            if pi == 0 and 0 < len(stages) < 3:
                warns.append(f"{pp}: an MVP usually needs 3 or more stages (skeleton, core flow, review)")
            if pi > 0 and hours > 20:
                warns.append(f"{pp}: one feature is {hours:g} hours; shrink it or split it into two phases")
            if pi > 0 and len(stages) > 5:
                warns.append(f"{pp}: {len(stages)} stages for one feature; split it into two phases")
        if not d.get("data_model"):
            warns.append("data_model is empty; prompts work better with it")
        if not d.get("risks"):
            warns.append("risks is empty")
    return errs, warns


# ---------------------------------------------------------------- html kit

CSS = """
:root{--bg:#f7f6f2;--fg:#1d2230;--mut:#5f6677;--card:#fff;--line:#e3e0d6;--acc:#245c43;--acc2:#e8f1ec;--warn:#9a5b00;--warnbg:#fff4e0;
--bad:#a82a1c;--info:#1d5aa8;--infobg:#e6f0fb;--code:#f0efe9}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#13151a;--fg:#e7e5de;--mut:#9aa1b0;--card:#1b1e25;--line:#2c313b;--acc:#7ad1a0;--acc2:#1e2c25;
--warn:#f0b35a;--warnbg:#2b2417;--bad:#ff8a7a;--info:#8bb8f0;--infobg:#1b2636;--code:#22262e}}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
a{color:var(--acc)}.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
header.hero{padding:34px 0 22px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)}
h1{margin:6px 0 4px;font-size:clamp(28px,5vw,42px);line-height:1.1}
.tag{color:var(--mut);margin:0 0 14px;font-size:18px}
.banner{background:var(--warnbg);color:var(--warn);border:1px solid var(--warn);border-radius:10px;padding:8px 12px;margin:12px 0;font-size:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-top:16px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:12px}
.stat small{display:block;color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.05em}
.stat b{display:block;font-size:17px;line-height:1.3;margin-top:2px}
nav.toc{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);overflow-x:auto;white-space:nowrap}
nav.toc a{display:inline-block;padding:10px 12px;text-decoration:none;font-size:14px;color:var(--mut)}
nav.toc a:hover{color:var(--acc)}
section{padding:26px 0 6px;scroll-margin-top:48px}section h2{font-size:22px;margin:0 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.card h3{margin:0 0 4px;font-size:17px}.card p{margin:6px 0}.mut{color:var(--mut)}
.badge{display:inline-block;font-size:11px;padding:1px 8px;border-radius:999px;border:1px solid var(--line);margin-left:6px;vertical-align:middle;color:var(--mut)}
.badge.confirmed{color:var(--acc);border-color:var(--acc);background:var(--acc2)}
.badge.reported,.badge.typical{color:var(--info);border-color:var(--info);background:var(--infobg)}
.badge.estimate{color:var(--warn);border-color:var(--warn);background:var(--warnbg)}
sup a{text-decoration:none;font-size:11px}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card)}
table{width:100%;border-collapse:collapse;font-size:14.5px}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--mut);font-weight:600;font-size:13px}
ul.clean{margin:0;padding-left:20px}.good li::marker{color:var(--acc)}.cons li::marker{color:var(--bad)}
.tl{border-left:2px solid var(--line);margin-left:6px;padding-left:16px}.tl .it{margin:0 0 14px;position:relative}
.tl .it:before{content:"";position:absolute;left:-23px;top:7px;width:10px;height:10px;border-radius:50%;background:var(--acc)}
.tl b{display:block}
pre.prompt{white-space:pre-wrap;background:var(--code);border:1px solid var(--line);border-radius:10px;padding:12px;font:13.5px/1.5 ui-monospace,Menlo,Consolas,monospace;margin:8px 0}
button{font:inherit;font-size:13px;padding:5px 12px;border-radius:8px;border:1px solid var(--acc);background:var(--acc2);color:var(--acc);cursor:pointer}
label.chk{display:flex;gap:8px;align-items:flex-start;margin:4px 0}
.prog{height:8px;background:var(--line);border-radius:99px;overflow:hidden;margin:8px 0}.prog i{display:block;height:100%;width:0;background:var(--acc);transition:width .3s}
.flow{counter-reset:s;list-style:none;padding:0;margin:0}.flow li{counter-increment:s;padding:6px 0 6px 34px;position:relative}
.flow li:before{content:counter(s);position:absolute;left:0;top:6px;width:24px;height:24px;border-radius:50%;background:var(--acc2);color:var(--acc);font-size:13px;display:grid;place-items:center}
footer{margin:40px 0;padding-top:16px;border-top:1px solid var(--line);color:var(--mut);font-size:13px}
.src li{word-break:break-all;font-size:13px}
@media print{nav.toc,button{display:none}body{background:#fff}}
"""

JS = """
const K=document.body.dataset.key||'rub';
function load(){try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return{}}}
function save(o){try{localStorage.setItem(K,JSON.stringify(o))}catch(e){}}
function sync(){const o=load();let n=0,t=0;document.querySelectorAll('input[data-id]').forEach(c=>{c.checked=!!o[c.dataset.id];t++;if(c.checked)n++});
 const p=document.getElementById('prog');if(p){p.style.width=(t?n*100/t:0)+'%';const l=document.getElementById('plabel');if(l)l.textContent=n+' of '+t+' done'}}
document.addEventListener('change',e=>{const c=e.target;if(c.dataset&&c.dataset.id){const o=load();o[c.dataset.id]=c.checked;save(o);sync()}});
document.addEventListener('click',e=>{const b=e.target.closest('button[data-copy]');if(!b)return;const t=document.getElementById(b.dataset.copy).innerText;
 const done=()=>{const x=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=x,1400)};
 if(navigator.clipboard){navigator.clipboard.writeText(t).then(done,()=>{})}else{const a=document.createElement('textarea');a.value=t;document.body.appendChild(a);a.select();try{document.execCommand('copy');done()}catch(_){}a.remove()}});
sync();
"""


class Sources:
    """Numbers each distinct URL so facts can show [1], [2] and the page can list them."""

    def __init__(self):
        self.urls: list[str] = []

    def refs(self, srcs) -> str:
        out = []
        for u in srcs or []:
            if not is_url(u):
                continue
            if u not in self.urls:
                self.urls.append(u)
            n = self.urls.index(u) + 1
            out.append(f'<a href="#src{n}">{n}</a>')
        return f"<sup>[{', '.join(out)}]</sup>" if out else ""

    def listing(self) -> str:
        items = "".join(f'<li id="src{i + 1}"><a href="{esc(u)}" rel="noopener noreferrer" target="_blank">{esc(u)}</a></li>'
                        for i, u in enumerate(self.urls))
        return f'<ol class="src">{items}</ol>' if items else '<p class="mut">No sources listed.</p>'


def page(title: str, key: str, body: str, nav: list[tuple[str, str]], hero: str, sample: bool) -> str:
    navhtml = "".join(f'<a href="#{esc(i)}">{esc(t)}</a>' for i, t in nav)
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    banner = ('<div class="banner"><b>Sample.</b> This page uses a fictional company to show the format. '
              'Facts here are not real.</div>') if sample else ""
    return ("<!doctype html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{esc(title)}</title><style>{CSS}</style></head><body data-key=\"{esc(key)}\">"
            f"<header class=hero><div class=wrap>{hero}{banner}</div></header>"
            f"<nav class=toc><div class=wrap>{navhtml}</div></nav><main class=wrap>{body}</main>"
            f"<footer class=wrap>Made with RUB (Research, Understand, Build) from public sources on "
            f"{dt.date.today().isoformat()}. Facts carry a confidence label and sources; verify anything important "
            f"before you rely on it.</footer><script>{JS}</script></body></html>")


def badge(conf: str) -> str:
    return f'<span class="badge {esc(conf)}">{esc(CONF_LABEL.get(conf, conf.title()))}</span>'


def fact_html(f: dict, S: Sources) -> str:
    if not isinstance(f, dict):
        return esc(f)
    c = f.get("confidence", "unknown")
    v = "Not publicly confirmed" if c == "unknown" else f.get("value", "")
    return f"{esc(v)}{badge(c) if c != 'confirmed' else ''}{S.refs(f.get('sources'))}"


def bullets(items, S: Sources, cls="") -> str:
    lis = []
    for it in items or []:
        if isinstance(it, dict):
            text = it.get("point") or it.get("tactic") or ""
            det = it.get("detail", "")
            lis.append(f"<li><b>{esc(text)}</b>{(' — ' + esc(det)) if det else ''}{S.refs(it.get('sources'))}</li>")
        else:
            lis.append(f"<li>{esc(it)}</li>")
    return f'<ul class="clean {cls}">{"".join(lis)}</ul>' if lis else ""


# ---------------------------------------------------------------- case study

def render_case(d: dict) -> str:
    S = Sources()
    snap, fund, mk = d.get("snapshot", {}), d.get("funding", {}), d.get("market", {})
    stat = lambda label, f: f'<div class=stat><small>{esc(label)}</small><b>{fact_html(f, S)}</b></div>' if f else ""
    hero = (f'<div class=eyebrow>Case study &middot; as of {esc(d.get("as_of", dt.date.today().isoformat()))}</div>'
            f'<h1>{esc(d["name"])}</h1><p class=tag>{esc(d.get("tagline", ""))}</p>'
            + (f'<a href="{esc(d["website"])}" rel="noopener noreferrer" target="_blank">{esc(d["website"])}</a>' if is_url(d.get("website")) else "")
            + '<div class=stats>'
            + stat("Founded", snap.get("founded")) + stat("Founders", snap.get("founders"))
            + stat("Total raised", fund.get("total_raised")) + stat("Valuation", fund.get("valuation"))
            + stat("Latest round", fund.get("latest_round")) + stat("Market position", mk.get("position")) + '</div>')
    nav, sec = [], []

    def add(id_, title, inner):
        if inner.strip():
            nav.append((id_, title))
            sec.append(f'<section id="{id_}"><h2>{esc(title)}</h2>{inner}</section>')

    rows = "".join(f"<tr><th>{esc(k.replace('_', ' ').title())}<td>{fact_html(v, S)}</tr>" for k, v in snap.items())
    add("overview", "At a glance",
        f'<div class=grid><div class=card><h3>The problem</h3><p>{esc(d.get("problem", ""))}</p></div>'
        f'<div class=card><h3>The solution</h3><p>{esc(d.get("solution", ""))}</p></div>'
        f'<div class=card><h3>Who it is for</h3><p>{esc(d.get("who_its_for", ""))}</p></div></div>'
        f'<p></p><table>{rows}</table>')
    feats = "".join(
        f'<div class=card><h3>{esc(f["name"])}</h3><p>{esc(f.get("what", ""))}</p>'
        f'<p><b>Why it matters:</b> {esc(f.get("why_it_matters", ""))}</p>'
        + (f'<p class=mut><b>How it works:</b> {esc(f["how_it_works"])}</p>' if f.get("how_it_works") else "")
        + f'{S.refs(f.get("sources"))}</div>' for f in d.get("features", []))
    add("features", "What they are building", f'<div class=grid>{feats}</div>')
    usp = "".join(f'<div class=card><h3>{esc(u.get("point", ""))}</h3><p>{esc(u.get("detail", ""))}</p>{S.refs(u.get("sources"))}</div>'
                  for u in d.get("usp", []))
    add("usp", "What makes it special (USP)", f'<div class=grid>{usp}</div>')
    bm = d.get("business_model", {})
    price = "".join(f"<tr><td>{esc(p.get('plan'))}<td>{esc(p.get('price'))}<td>{esc(p.get('notes', ''))}</tr>" for p in bm.get("pricing", []))
    add("business", "Business model",
        f'<p><b>How it makes money:</b> {esc(bm.get("revenue", ""))}</p>'
        + (f'<p><b>Value metric:</b> {esc(bm["value_metric"])}</p>' if bm.get("value_metric") else "")
        + (f'<table><tr><th>Plan<th>Price<th>Notes</tr>{price}</table>' if price else "")
        + (f'<p class=mut>{esc(bm["unit_economics_note"])}</p>' if bm.get("unit_economics_note") else ""))
    rounds = "".join(f"<tr><td>{esc(r.get('round'))}<td>{esc(r.get('date'))}<td>{esc(r.get('amount'))}"
                     f"<td>{esc(r.get('lead_investors', ''))}<td>{esc(r.get('other_investors', ''))}{S.refs(r.get('sources'))}</tr>"
                     for r in fund.get("rounds", []))
    add("funding", "Funding and why investors backed it",
        (f'<table><tr><th>Round<th>Date<th>Amount<th>Lead<th>Others</tr>{rounds}</table>' if rounds else "")
        + ("<h3>Why they got funded</h3>" + bullets(fund.get("why_funded"), S, "good") if fund.get("why_funded") else ""))
    add("market", "Market position and why they lead",
        (f"<p><b>Position:</b> {fact_html(mk['position'], S)}</p>" if mk.get("position") else "")
        + ("<h3>Why they are ahead</h3>" + bullets(mk.get("why_leading"), S, "good") if mk.get("why_leading") else "")
        + ("<h3>Traction</h3>" + bullets(mk.get("traction"), S) if mk.get("traction") else ""))
    comps = mk.get("competitors", [])
    glance = "".join(f"<tr><td><b>{esc(c.get('name'))}</b><td><span class=badge>{esc(c.get('angle'))}</span>"
                     f"<td>{esc(c.get('how_they_differentiate', ''))}<td>{esc(c.get('pricing', ''))}</tr>" for c in comps)
    cards = ""
    for c in comps:
        name = (f'<a href="{esc(c["website"])}" rel="noopener noreferrer" target="_blank">{esc(c["name"])}</a>'
                if is_url(c.get("website")) else esc(c.get("name")))
        cards += (f'<div class=card><h3>{name} <span class=badge>{esc(c.get("angle"))}</span></h3>'
                  f'<p>{esc(c.get("what_they_do", ""))}</p>'
                  f'<p><b>How they stand out:</b> {esc(c.get("how_they_differentiate", ""))}</p>'
                  + (f'<p><b>Pricing:</b> {esc(c["pricing"])}</p>' if c.get("pricing") else "")
                  + (f'<p><b>Traction:</b> {esc(c["traction"])}</p>' if c.get("traction") else "")
                  + (f'<p><b>Strong at</b></p>{bullets(c.get("strengths"), S, "good")}' if c.get("strengths") else "")
                  + (f'<p><b>Weak at</b></p>{bullets(c.get("weaknesses"), S, "cons")}' if c.get("weaknesses") else "")
                  + f'<p>{S.refs(c.get("sources"))}</p></div>')
    ws = "".join(f"<tr><td>{esc(w.get('gap'))}<td>{esc(w.get('evidence', ''))}{S.refs(w.get('sources'))}</tr>" for w in mk.get("white_space") or [])
    add("competitors", "Competitors and how they differentiate",
        (f'<p>{esc(mk["differentiation_summary"])}</p>' if mk.get("differentiation_summary") else "")
        + (f'<table><tr><th>Competitor<th>Angle<th>How they stand out<th>Pricing</tr>{glance}</table><p></p>' if glance else "")
        + (f'<div class=grid>{cards}</div>' if cards else "")
        + (f'<h3>White space: what nobody serves well</h3><table><tr><th>Gap<th>Evidence</tr>{ws}</table>' if ws else ""))
    add("growth", "How they got customers", bullets(d.get("growth"), S))
    add("strengths", "What they do well", bullets(d.get("strengths"), S, "good"))
    add("drawbacks", "Drawbacks and risks", bullets(d.get("drawbacks"), S, "cons"))
    trows = "".join(f"<tr><td>{esc(t.get('layer'))}<td>{esc(t.get('choice'))}{badge(t.get('confidence', 'typical'))}"
                    f"<td>{esc(t.get('note', ''))}{S.refs(t.get('evidence'))}</tr>" for t in d.get("tech", []))
    add("tech", "Technology (what is public vs typical)",
        (f'<table><tr><th>Layer<th>Choice<th>Note</tr>{trows}</table>'
         '<p class=mut>"Confirmed" comes from the company\'s own pages, docs or job posts. "Typical" is the usual approach for this kind of product; '
         'RUB does not look inside private systems.</p>') if trows else "")
    tl = "".join(f'<div class=it><b>{esc(t.get("date"))}</b>{esc(t.get("event"))}{S.refs(t.get("sources"))}</div>' for t in d.get("timeline", []))
    add("timeline", "Timeline", f'<div class=tl>{tl}</div>' if tl else "")
    opp = "".join(f"<tr><td>{esc(o.get('gap'))}<td>{esc(o.get('how_to_win', ''))}</tr>" for o in d.get("opportunities", []))
    add("opportunities", "Where you could do better", f'<table><tr><th>Gap<th>How to win</tr>{opp}</table>' if opp else "")
    add("sources", "Sources", S.listing())
    return page(f'{d["name"]} case study', "case-" + slug(d["name"]), "".join(sec), nav, hero, bool(d.get("sample")))


# ---------------------------------------------------------------- learn plan

def render_learn(d: dict) -> str:
    total = sum(t.get("hours", 0) for w in d["weeks"] for t in w["topics"])
    hero = (f'<div class=eyebrow>Learn plan &middot; {esc(d.get("level", ""))}</div><h1>Learn to build {esc(d["product"])}</h1>'
            f'<p class=tag>{esc(d["goal"])}</p><div class=stats>'
            f'<div class=stat><small>Weeks</small><b>{len(d["weeks"])}</b></div>'
            f'<div class=stat><small>Total hours</small><b>{total:g}</b></div>'
            f'<div class=stat><small>Pace</small><b>{d["hours_per_week"]:g} h / week</b></div></div>'
            '<div class=prog><i id=prog></i></div><div class=mut id=plabel></div>')
    nav, sec = [], []
    for w in d["weeks"]:
        wid = f"w{w.get('week')}"
        nav.append((wid, f"Week {w.get('week')}"))
        tops = ""
        for ti, t in enumerate(w["topics"]):
            cid = f"{wid}-{ti}"
            res = "".join(f'<li><a href="{esc(r["url"])}" rel="noopener noreferrer" target="_blank">{esc(r["title"])}</a>'
                          f'<span class=badge>{esc(r["kind"])}</span></li>' for r in t.get("resources", []))
            tops += (f'<div class=card><label class=chk><input type=checkbox data-id="{esc(cid)}"><span><b>{esc(t["topic"])}</b> '
                     f'<span class=badge>{t["hours"]:g} h</span></span></label>'
                     f'<p><b>Why you need it:</b> {esc(t["why"])}</p><p><b>Practice:</b> {esc(t["exercise"])}</p>'
                     + (f'<ul class=clean>{res}</ul>' if res else "") + '</div>')
        sec.append(f'<section id="{wid}"><h2>Week {esc(w.get("week"))}: {esc(w.get("theme", ""))}</h2>'
                   f'<div class=grid>{tops}</div>'
                   + (f'<p><b>Milestone:</b> {esc(w["milestone"])}</p>' if w.get("milestone") else "") + '</section>')
    if d.get("concepts"):
        nav.append(("concepts", "Key terms"))
        sec.append('<section id="concepts"><h2>Key terms</h2><table><tr><th>Term<th>In plain words</tr>'
                   + "".join(f"<tr><td>{esc(c['term'])}<td>{esc(c['plain'])}</tr>" for c in d["concepts"]) + '</table></section>')
    if d.get("skip_for_now"):
        nav.append(("skip", "Skip for now"))
        sec.append('<section id="skip"><h2>Skip for now</h2><p class=mut>You do not need these to ship the first version.</p>'
                   + bullets(d["skip_for_now"], Sources()) + '</section>')
    return page(f'Learn plan: {d["product"]}', "learn-" + slug(d["product"]), "".join(sec), nav, hero, bool(d.get("sample")))


# ---------------------------------------------------------------- build plan

def phase_hours(p: dict) -> float:
    return sum(s["hours"] for s in p["stages"])


def context_prompt(d: dict) -> str:
    st = "\n".join(f"- {k}: {v['choice']}" for k, v in d.get("stack", {}).items())
    dm = "\n".join(f"- {e['entity']}({', '.join(e['fields'])})" for e in d.get("data_model", []))
    api = "\n".join(f"- {a['method']} {a['path']}: {a['purpose']}" for a in d.get("api", []))
    road = "\n".join(f"- Phase {i}: {p['name']}" for i, p in enumerate(d["phases"], 1))
    scope = d.get("scope", {})
    return (f"You are helping me build my own product: {d['product']}.\n\n{d['summary']}\n\n"
            f"Stack:\n{st}\n\n"
            + (f"Data model:\n{dm}\n\n" if dm else "") + (f"API:\n{api}\n\n" if api else "")
            + f"Roadmap (we build one phase at a time, MVP first, then one feature per phase):\n{road}\n\n"
            + (f"In the MVP: {'; '.join(scope.get('in', []))}\n" if scope.get("in") else "")
            + (f"Not yet: {'; '.join(scope.get('out', []))}\n" if scope.get("out") else "")
            + "\nRules: build one phase and one stage at a time; never build features from a later phase early; keep changes small; "
              "keep the app working and the tests passing at the end of every stage; explain each file in one line; "
              "record what is done in PROGRESS.md; stop when the stage's acceptance checks pass. Write original code; do not copy "
              "any company's code, design, text or brand.")


def phase_brief(d: dict, i: int) -> str:
    p = d["phases"][i - 1]
    if p["kind"] == "mvp":
        head = (f"We are starting Phase {i}, the MVP of {d['product']}: {p['name']}.\nGoal: {p['goal']}\n"
                "Build only the smallest version that meets this goal. Anything outside the MVP scope waits for a later phase.")
    else:
        head = (f"The earlier phases are working. We are starting Phase {i}: add ONE feature, {p['feature']}.\nGoal: {p['goal']}\n"
                f"Why now: {p['why_next']}\n"
                "Read the existing code and PROGRESS.md first. Do not rewrite or reorganise earlier features; if an earlier part must "
                "change, explain why before you change it.")
    return (head + "\nWork through this phase's stages one at a time. After each stage run the tests, check that earlier features "
            "still work, and update PROGRESS.md. Stop when the stage's acceptance checks pass.")


def render_build(d: dict) -> str:
    phases = d["phases"]
    nstages = sum(len(p["stages"]) for p in phases)
    total = sum(phase_hours(p) for p in phases)
    hero = (f'<div class=eyebrow>Build plan &middot; phase by phase</div><h1>Build {esc(d["product"])}</h1><p class=tag>{esc(d["summary"])}</p>'
            f'<div class=stats><div class=stat><small>Phases</small><b>{len(phases)}</b></div>'
            f'<div class=stat><small>MVP</small><b>{phase_hours(phases[0]):g} h</b></div>'
            f'<div class=stat><small>All phases</small><b>{total:g} h &middot; {nstages} stages</b></div>'
            f'<div class=stat><small>Stack</small><b>{esc(d["stack"]["frontend"]["choice"].split(" (")[0])} + {esc(d["stack"]["backend"]["choice"].split(" (")[0])}</b></div></div>'
            '<div class=prog><i id=prog></i></div><div class=mut id=plabel></div>')
    nav, sec = [], []

    def add(id_, title, inner):
        if inner.strip():
            nav.append((id_, title))
            sec.append(f'<section id="{id_}"><h2>{esc(title)}</h2>{inner}</section>')

    sc = d.get("scope", {})
    add("scope", "MVP scope", f'<div class=grid><div class=card><h3>In the MVP</h3>{bullets(sc.get("in"), Sources(), "good")}</div>'
        f'<div class=card><h3>Later phases</h3>{bullets(sc.get("out"), Sources())}</div></div>' if sc else "")
    road = ""
    for i, p in enumerate(phases, 1):
        kind = "MVP" if p["kind"] == "mvp" else "Feature"
        why = p.get("why_next") or p.get("user_value", "")
        road += (f'<div class=card><h3><a href="#ph{i}">Phase {i}: {esc(p["name"])}</a> <span class=badge>{kind}</span> '
                 f'<span class=badge>{phase_hours(p):g} h</span></h3><p>{esc(p["goal"])}</p>'
                 + (f'<p class=mut>{esc(why)}</p>' if why else "") + '</div>')
    add("roadmap", "Roadmap", f'<p class=mut>Build the MVP first. Then add one feature at a time. Do not start a phase until the previous phase\'s '
        f'"move on when" checks are ticked.</p><div class=grid>{road}</div>')
    rows = "".join(f"<tr><td>{esc(k.title())}<td><b>{esc(v['choice'])}</b><td>{esc(v['why'])}<td class=mut>{esc(v.get('alternatives', ''))}</tr>"
                   for k, v in d["stack"].items())
    add("stack", "Stack", f'<table><tr><th>Layer<th>Choice<th>Why<th>Alternatives</tr>{rows}</table>')
    arch = d.get("architecture", {})
    comps = "".join(f"<tr><td><b>{esc(c['name'])}</b><td>{esc(c['role'])}</tr>" for c in arch.get("components", []))
    flows = "".join(f'<div class=card><h3>{esc(f["name"])}</h3><ol class=flow>' + "".join(f"<li>{esc(s)}</li>" for s in f["steps"]) + '</ol></div>'
                    for f in arch.get("flows", []))
    add("architecture", "Architecture",
        (f'<table><tr><th>Part<th>Job</tr>{comps}</table><p></p>' if comps else "") + (f'<div class=grid>{flows}</div>' if flows else ""))
    dm = "".join(f'<div class=card><h3>{esc(e["entity"])}</h3><p><code>{esc(", ".join(e["fields"]))}</code></p>'
                 + (f'<p class=mut>{esc(e["notes"])}</p>' if e.get("notes") else "") + '</div>' for e in d.get("data_model", []))
    add("data", "Data model", f'<div class=grid>{dm}</div>' if dm else "")
    api = "".join(f"<tr><td><code>{esc(a['method'])}</code><td><code>{esc(a['path'])}</code><td>{esc(a['purpose'])}</tr>" for a in d.get("api", []))
    add("api", "API", f'<table><tr><th>Method<th>Path<th>Purpose</tr>{api}</table>' if api else "")
    ctx = context_prompt(d)
    add("start", "Step 0: give your AI the project context",
        '<div class=card><p class=mut>Paste this first in Claude Code, Cursor or any coding assistant. Then, for each phase, paste the phase brief, '
        'then its stage prompts in order.</p>'
        f'<pre class=prompt id="p0">{esc(ctx)}</pre><button data-copy="p0">Copy</button></div>')
    for i, p in enumerate(phases, 1):
        kind = "MVP" if p["kind"] == "mvp" else "Feature"
        intro = f'<p><b>Goal:</b> {esc(p["goal"])}</p>'
        if p.get("feature"):
            intro += f'<p><b>The one feature:</b> {esc(p["feature"])}</p>'
        if p.get("why_next"):
            intro += f'<p><b>Why this is next:</b> {esc(p["why_next"])}</p>'
        if p.get("user_value"):
            intro += f'<p><b>Value to the user:</b> {esc(p["user_value"])}</p>'
        body = (intro + f'<div class=card><h3>Phase {i} brief</h3><p class=mut>Paste this at the start of the phase.</p>'
                f'<pre class=prompt id="pb{i}">{esc(phase_brief(d, i))}</pre><button data-copy="pb{i}">Copy phase brief</button></div>')
        for j, s in enumerate(p["stages"], 1):
            learn = (f'<p class=mut>Learn first: {esc(", ".join(s["learn_first"]))}</p>' if s.get("learn_first") else "")
            acc = "".join(f'<label class=chk><input type=checkbox data-id="{esc(s["id"])}-a{ai}"><span>{esc(a)}</span></label>'
                          for ai, a in enumerate(s["acceptance"]))
            body += (f'<div class=card id="{esc(s["id"])}"><h3>Stage {i}.{j}: {esc(s["name"])} <span class=badge>{s["hours"]:g} h</span></h3>'
                     f'<p><b>Goal:</b> {esc(s["goal"])}<br><b>You get:</b> {esc(s["deliverable"])}</p>{learn}'
                     f'<pre class=prompt id="p-{esc(s["id"])}">{esc(s["prompt"])}</pre><button data-copy="p-{esc(s["id"])}">Copy prompt</button>'
                     f'<p><b>Done when:</b></p>{acc}</div>')
        exits = "".join(f'<label class=chk><input type=checkbox data-id="{esc(p["id"])}-x{xi}"><span>{esc(x)}</span></label>'
                        for xi, x in enumerate(p["exit_criteria"]))
        body += (f'<div class=card><h3>Move on when</h3><p class=mut>Ship this phase to real users and check these before starting '
                 f'{"the next feature" if i < len(phases) else "anything new"}.</p>{exits}</div>')
        add(f"ph{i}", f"Phase {i} ({kind}): {p['name']}", body)
    add("launch", "Before you show it to users", bullets(d.get("launch_checklist"), Sources()))
    add("risks", "Risks to watch", bullets(d.get("risks"), Sources(), "cons"))
    return page(f'Build plan: {d["product"]}', "build-" + slug(d["product"]), "".join(sec), nav, hero, bool(d.get("sample")))


def export_prompts(d: dict, out: Path) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    written = []
    p0 = out / "00-project-context.md"
    p0.write_text("# Step 0: project context\n\nPaste this first. Then work phase by phase: the phase brief, then each stage prompt in order.\n\n```text\n"
                  + context_prompt(d) + "\n```\n", encoding="utf-8")
    written.append(p0)
    allp = [f"# {d['product']}: all prompts\n", "## Step 0: project context\n", "```text\n" + context_prompt(d) + "\n```\n"]
    for i, p in enumerate(d["phases"], 1):
        kind = "MVP" if p["kind"] == "mvp" else "Feature"
        brief = (f"# Phase {i} ({kind}): {p['name']}\n\n**Goal:** {p['goal']}  \n"
                 + (f"**One feature:** {p['feature']}  \n" if p.get("feature") else "")
                 + (f"**Why next:** {p['why_next']}  \n" if p.get("why_next") else "")
                 + f"**Estimated hours:** {phase_hours(p):g}\n\n## Phase brief (paste first)\n\n```text\n{phase_brief(d, i)}\n```\n\n"
                 "## Move on when\n\n" + "\n".join(f"- [ ] {x}" for x in p["exit_criteria"]) + "\n")
        f = out / f"p{i}-00-phase-brief.md"
        f.write_text(brief, encoding="utf-8")
        written.append(f)
        allp.append(brief.replace("# Phase", "## Phase", 1))
        for j, s in enumerate(p["stages"], 1):
            body = (f"# Stage {i}.{j}: {s['name']}\n\n**Goal:** {s['goal']}  \n**You get:** {s['deliverable']}  \n**Estimated hours:** {s['hours']:g}\n\n"
                    + (f"**Learn first:** {', '.join(s['learn_first'])}\n\n" if s.get("learn_first") else "")
                    + "## Prompt\n\n```text\n" + s["prompt"] + "\n```\n\n## Done when\n\n" + "\n".join(f"- [ ] {a}" for a in s["acceptance"]) + "\n")
            f = out / f"p{i}-{j:02d}-{slug(s['name'])}.md"
            f.write_text(body, encoding="utf-8")
            written.append(f)
            allp.append(body.replace("# Stage", "### Stage", 1))
    pa = out / "PROMPTS.md"
    pa.write_text("\n".join(allp), encoding="utf-8")
    written.append(pa)
    return written


RENDER = {"case": (render_case, "CASESTUDY.html"), "learn": (render_learn, "LEARN-PLAN.html"), "build": (render_build, "BUILD-PLAN.html")}


def load_json(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"error: {path} not found")
    except ValueError as e:
        sys.exit(f"error: {path} is not valid JSON: {e}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("template"); s.add_argument("kind", choices=TEMPLATES)
    s = sub.add_parser("check"); s.add_argument("kind", choices=TEMPLATES); s.add_argument("file")
    s = sub.add_parser("render"); s.add_argument("kind", choices=TEMPLATES); s.add_argument("file"); s.add_argument("--out")
    s = sub.add_parser("export"); s.add_argument("file"); s.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "template":
        print(json.dumps(TEMPLATES[a.kind], indent=2, ensure_ascii=False))
        return 0
    data = load_json(a.file)
    kind = a.kind if a.cmd != "export" else "build"
    errs, warns = problems(kind, data)
    for e in errs:
        print(f"ERROR   {e}")
    for w in warns:
        print(f"WARN    {w}")
    if errs:
        print(f"{len(errs)} errors, {len(warns)} warnings: fix the errors first.")
        return 1
    if a.cmd == "check":
        print(f"ok: {len(warns)} warnings")
        return 0
    if a.cmd == "render":
        fn, default = RENDER[a.kind]
        out = Path(a.out) if a.out else Path(a.file).with_name(default)
        out.write_text(fn(data), encoding="utf-8")
        print(f"wrote {out}")
        return 0
    files = export_prompts(data, Path(a.out))
    print(f"wrote {len(files)} prompt files to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
