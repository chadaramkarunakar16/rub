# Step 0: project context

Paste this first. Then work phase by phase: the phase brief, then each stage prompt in order.

```text
You are helping me build my own product: Sampleo.

A mobile-first app where a field rep records a voice note after a visit and it becomes a structured CRM record.

Stack:
- frontend: Next.js (responsive web app / PWA)
- backend: FastAPI (Python)
- database: PostgreSQL (Supabase)
- auth: Supabase Auth
- ai: Speech-to-text API + LLM with JSON output
- hosting: Vercel + Render

Data model:
- users(id, email, team_id)
- visits(id, user_id, customer_name, audio_url, transcript, created_at)
- records(id, visit_id, fields_json, status)

API:
- POST /visits: Upload audio and create a visit
- GET /visits: List my visits
- PATCH /records/{id}: Edit and confirm a record

Roadmap (we build one phase at a time, MVP first, then one feature per phase):
- Phase 1: Voice note to a confirmed record
- Phase 2: Manager daily digest
- Phase 3: Offline capture

In the MVP: Record voice note; Transcribe; Extract fields; Show, edit and confirm the record
Not yet: Manager daily digest (phase 2); Offline capture (phase 3); Real CRM integrations (use CSV export first); Team admin

Rules: build one phase and one stage at a time; never build features from a later phase early; keep changes small; keep the app working and the tests passing at the end of every stage; explain each file in one line; record what is done in PROGRESS.md; stop when the stage's acceptance checks pass. Write original code; do not copy any company's code, design, text or brand.
```
