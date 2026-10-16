#!/usr/bin/env python3
"""repomap.py - map a public open-source repo (or your own) so it can be studied.

Reads a local folder (clone it first with `git clone --depth 1 <url> <dir>`) and writes a
plain-language fact sheet: license, languages, stack, folder layout, entry points, data
model files, routes/API files, tests, CI and deployment. It only reads files; it never runs them.

Usage:
  python repomap.py map <dir> [--out FILE] [--json]
"""
import argparse, json, os, re, sys
from collections import Counter

SKIP = {".git", "node_modules", "vendor", "dist", "build", ".next", "target", "__pycache__",
        ".venv", "venv", ".idea", ".vscode", "coverage", ".cache", ".turbo"}
LANGS = {".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
         ".go": "Go", ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift", ".rb": "Ruby",
         ".php": "PHP", ".cs": "C#", ".c": "C", ".h": "C", ".cpp": "C++", ".cc": "C++", ".dart": "Dart",
         ".ex": "Elixir", ".exs": "Elixir", ".scala": "Scala", ".lua": "Lua", ".sh": "Shell",
         ".sql": "SQL", ".html": "HTML", ".css": "CSS", ".scss": "CSS", ".vue": "Vue", ".svelte": "Svelte"}
MANIFESTS = {"package.json": "Node/JS", "requirements.txt": "Python", "pyproject.toml": "Python",
             "Pipfile": "Python", "go.mod": "Go", "Cargo.toml": "Rust", "pom.xml": "Java (Maven)",
             "build.gradle": "Java/Kotlin (Gradle)", "build.gradle.kts": "Kotlin (Gradle)",
             "Gemfile": "Ruby", "composer.json": "PHP", "pubspec.yaml": "Dart/Flutter",
             "mix.exs": "Elixir", "Package.swift": "Swift"}
FRAMEWORKS = {  # dependency name -> label
    "react": "React", "next": "Next.js", "vue": "Vue", "nuxt": "Nuxt", "svelte": "Svelte", "@sveltejs/kit": "SvelteKit",
    "express": "Express", "fastify": "Fastify", "@nestjs/core": "NestJS", "hono": "Hono", "electron": "Electron",
    "react-native": "React Native", "expo": "Expo", "tailwindcss": "Tailwind CSS", "prisma": "Prisma",
    "@prisma/client": "Prisma", "drizzle-orm": "Drizzle", "mongoose": "MongoDB (mongoose)", "pg": "PostgreSQL",
    "redis": "Redis", "socket.io": "WebSockets (socket.io)", "ws": "WebSockets", "graphql": "GraphQL",
    "@trpc/server": "tRPC", "stripe": "Stripe payments", "openai": "OpenAI API", "@anthropic-ai/sdk": "Anthropic API",
    "langchain": "LangChain", "django": "Django", "flask": "Flask", "fastapi": "FastAPI", "sqlalchemy": "SQLAlchemy",
    "celery": "Celery", "pydantic": "Pydantic", "torch": "PyTorch", "transformers": "Hugging Face Transformers",
    "numpy": "NumPy", "pandas": "pandas", "gin-gonic/gin": "Gin (Go)", "gorilla/mux": "gorilla/mux",
    "labstack/echo": "Echo (Go)", "actix-web": "Actix", "axum": "Axum", "tokio": "Tokio", "rails": "Rails",
    "laravel/framework": "Laravel", "supabase": "Supabase", "@supabase/supabase-js": "Supabase", "firebase": "Firebase",
}
ENTRY_NAMES = {"main.py", "app.py", "manage.py", "wsgi.py", "asgi.py", "server.py", "index.js", "index.ts",
               "server.js", "server.ts", "app.js", "app.ts", "main.go", "main.rs", "lib.rs", "Main.java",
               "Program.cs", "main.dart", "main.ts", "main.js"}
MODEL_HINT = re.compile(r"(model|schema|entity|migration|prisma|\.sql$)", re.I)
ROUTE_HINT = re.compile(r"(route|router|controller|endpoint|api|handler|view)s?", re.I)
LICENSES = [("MIT", r"permission is hereby granted, free of charge"), ("Apache-2.0", r"apache license"),
            ("GPL-3.0", r"gnu general public license[\s\S]{0,200}version 3"), ("GPL-2.0", r"gnu general public license[\s\S]{0,200}version 2"),
            ("AGPL-3.0", r"gnu affero"), ("LGPL", r"gnu lesser general public"), ("MPL-2.0", r"mozilla public license"),
            ("BSD", r"redistribution and use in source and binary forms"), ("Unlicense", r"this is free and unencumbered software"),
            ("ISC", r"permission to use, copy, modify, and/or distribute")]
LICENSE_NOTE = {"MIT": "permissive: you may reuse code with the notice kept", "Apache-2.0": "permissive with patent grant; keep notices",
                "BSD": "permissive; keep notices", "ISC": "permissive; keep notices", "Unlicense": "public domain style",
                "GPL-3.0": "copyleft: code you derive from it must also be GPL", "GPL-2.0": "copyleft: derived code must also be GPL",
                "AGPL-3.0": "strong copyleft, also covers network use: do not copy into a closed product",
                "LGPL": "weak copyleft for libraries", "MPL-2.0": "file-level copyleft"}


def walk(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".git")]
        for f in files:
            yield os.path.join(d, f)


def read(path, limit=200_000):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            return fh.read(limit)
    except OSError:
        return ""


def detect_license(root):
    for name in os.listdir(root):
        if name.lower().startswith(("license", "licence", "copying", "unlicense")):
            text = read(os.path.join(root, name), 20000).lower()
            for label, pat in LICENSES:
                if re.search(pat, text):
                    return label, name
            return "unrecognised", name
    return "none found", None


def deps_from(path, name):
    text = read(path)
    found = set()
    if name == "package.json":
        try:
            j = json.loads(text)
            for k in ("dependencies", "devDependencies", "peerDependencies"):
                found |= set((j.get(k) or {}).keys())
        except ValueError:
            pass
    else:
        low = text.lower()
        for key in FRAMEWORKS:
            if re.search(r"(?<![\w-])" + re.escape(key.lower()) + r"(?![\w-])", low):
                found.add(key)
    return found


def build(root):
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        sys.exit(f"not a folder: {root}")
    files = list(walk(root))
    ext = Counter()
    lines_by_lang = Counter()
    for f in files:
        lang = LANGS.get(os.path.splitext(f)[1].lower())
        if lang:
            ext[lang] += 1
            if ext[lang] <= 400:  # sample for speed
                lines_by_lang[lang] += read(f, 400_000).count("\n")
    manifests, deps = [], set()
    for f in files:
        base = os.path.basename(f)
        if base in MANIFESTS and os.path.dirname(f).count(os.sep) - root.count(os.sep) <= 3:
            manifests.append((os.path.relpath(f, root), MANIFESTS[base]))
            deps |= deps_from(f, base)
    stack = sorted({FRAMEWORKS[d] for d in deps if d in FRAMEWORKS})
    rel = lambda p: os.path.relpath(p, root).replace(os.sep, "/")
    entries = [rel(f) for f in files if os.path.basename(f) in ENTRY_NAMES][:15]
    models = [rel(f) for f in files if MODEL_HINT.search(rel(f)) and os.path.splitext(f)[1].lower() in (".py", ".ts", ".js", ".go", ".rs", ".prisma", ".sql", ".rb", ".java", ".kt")][:25]
    routes = [rel(f) for f in files if ROUTE_HINT.search(os.path.basename(f)) and os.path.splitext(f)[1].lower() in (".py", ".ts", ".js", ".go", ".rs", ".rb", ".java", ".kt", ".php")][:25]
    tests = [rel(f) for f in files if re.search(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec)\.", rel(f))]
    ci = [rel(f) for f in files if rel(f).startswith(".github/workflows/") or rel(f) in (".gitlab-ci.yml", "Jenkinsfile", ".circleci/config.yml")]
    deploy = [rel(f) for f in files if os.path.basename(f) in ("Dockerfile", "docker-compose.yml", "docker-compose.yaml", "vercel.json", "fly.toml", "netlify.toml", "render.yaml", "Procfile", "serverless.yml")]
    top = []
    for name in sorted(os.listdir(root)):
        if name in SKIP or name.startswith(".git"):
            continue
        p = os.path.join(root, name)
        count = sum(1 for _ in walk(p)) if os.path.isdir(p) else 1
        top.append((name + ("/" if os.path.isdir(p) else ""), count))
    lic, lic_file = detect_license(root)
    readme = next((n for n in os.listdir(root) if n.lower().startswith("readme")), None)
    return {"name": os.path.basename(root), "files": len(files), "license": lic, "license_file": lic_file,
            "license_note": LICENSE_NOTE.get(lic, "read the licence file before reusing any code"),
            "languages": dict(ext.most_common(8)), "approx_lines": dict(lines_by_lang.most_common(8)),
            "manifests": manifests, "stack": stack, "entry_points": entries, "data_model_files": models,
            "route_files": routes, "test_files": len(tests), "ci": ci, "deploy": deploy, "top_level": top,
            "readme": readme}


def render(m):
    out = [f"# Repo map: {m['name']}", "",
           f"- **Files:** {m['files']}  |  **README:** {m['readme'] or 'none'}",
           f"- **Licence:** {m['license']} ({m['license_file'] or 'no file'}): {m['license_note']}", "",
           "## Languages (files)", ""]
    out += [f"- {k}: {v} files, about {m['approx_lines'].get(k, 0):,} lines" for k, v in m["languages"].items()] or ["- none detected"]
    out += ["", "## Stack detected from dependencies", ""] + ([f"- {s}" for s in m["stack"]] or ["- nothing recognised"])
    out += ["", "## Package manifests", ""] + ([f"- `{p}` ({k})" for p, k in m["manifests"]] or ["- none"])
    out += ["", "## Top-level layout (path, files inside)", ""] + [f"- `{n}` {c}" for n, c in m["top_level"]]
    for title, key in (("Entry points", "entry_points"), ("Data model / schema files", "data_model_files"),
                       ("Routes / API / handler files", "route_files"), ("CI", "ci"), ("Deployment config", "deploy")):
        out += ["", f"## {title}", ""] + ([f"- `{x}`" for x in m[key]] or ["- none found"])
    out += ["", f"## Tests", "", f"- {m['test_files']} test files", "",
            "_Facts only. Reading order, explanation and build lessons come from the cartographer._"]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map")
    m.add_argument("dir")
    m.add_argument("--out")
    m.add_argument("--json", action="store_true")
    a = ap.parse_args()
    data = build(a.dir)
    text = json.dumps(data, indent=2) if a.json else render(data)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {a.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
