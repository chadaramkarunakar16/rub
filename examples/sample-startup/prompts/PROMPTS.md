# Sampleo: all prompts

## Step 0: project context

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

## Phase 1 (MVP): Voice note to a confirmed record

**Goal:** One rep can record a visit, get a structured record, fix it and confirm it  
**Estimated hours:** 24

## Phase brief (paste first)

```text
We are starting Phase 1, the MVP of Sampleo: Voice note to a confirmed record.
Goal: One rep can record a visit, get a structured record, fix it and confirm it
Build only the smallest version that meets this goal. Anything outside the MVP scope waits for a later phase.
Work through this phase's stages one at a time. After each stage run the tests, check that earlier features still work, and update PROGRESS.md. Stop when the stage's acceptance checks pass.
```

## Move on when

- [ ] 5 real reps use it on real visits for a week
- [ ] At least 8 of 10 records need one edit or fewer
- [ ] Capture takes under 2 minutes end to end
- [ ] Cost per visit is logged and within your budget

### Stage 1.1: Project skeleton and auth

**Goal:** Running app with login  
**You get:** Login page and an empty dashboard, deployed  
**Estimated hours:** 4

**Learn first:** HTTP and REST

## Prompt

```text
Create a Next.js app with Supabase email authentication. Add a protected /dashboard page that shows the signed-in user's email. Use TypeScript and a clean, mobile-first layout. Explain each file you create in one line. Stop when the acceptance checks pass.
```

## Done when

- [ ] I can sign up, sign in and sign out
- [ ] Dashboard is unreachable when signed out

### Stage 1.2: Database and visits API

**Goal:** Create and list visits  
**You get:** visits table and two endpoints  
**Estimated hours:** 5

**Learn first:** SQL and a database

## Prompt

```text
Add the visits and records tables from the data model using migrations. Build POST /visits and GET /visits in FastAPI, checking the signed-in user. Add tests for both endpoints. Stop when the acceptance checks pass.
```

## Done when

- [ ] A visit created by user A is not visible to user B
- [ ] Tests pass

### Stage 1.3: Record and upload audio

**Goal:** Record in the browser and upload  
**You get:** Record button, upload progress, saved audio  
**Estimated hours:** 5

## Prompt

```text
Add a record screen that captures microphone audio with the MediaRecorder API, shows a timer, and uploads the file to POST /visits. Handle denied microphone permission with a clear message. Stop when the acceptance checks pass.
```

## Done when

- [ ] Audio plays back from storage
- [ ] Permission denied shows a helpful message

### Stage 1.4: Transcribe and extract

**Goal:** Turn audio into structured fields  
**You get:** Worker that fills records.fields_json  
**Estimated hours:** 6

**Learn first:** Calling a speech-to-text API, Prompting for JSON output

## Prompt

```text
Add a background job that transcribes a visit's audio with a speech-to-text API and then calls an LLM to extract customer, outcome, next step and follow-up date as JSON matching a fixed schema. Validate the JSON and retry once on failure. Log the cost per visit. Stop when the acceptance checks pass.
```

## Done when

- [ ] 20 sample recordings produce valid JSON at least 90% of the time
- [ ] Failures are visible in the UI

### Stage 1.5: Review and confirm

**Goal:** Let the rep fix and approve a record  
**You get:** Edit screen with a Confirm button  
**Estimated hours:** 4

## Prompt

```text
Build a review screen that shows the extracted fields with inline editing and a Confirm button that sets the record status to confirmed. Confirmed records must not change silently. Keep the UI minimal. Stop when the acceptance checks pass.
```

## Done when

- [ ] Confirmed records are locked until the rep re-opens them
- [ ] Edits are saved and shown after a refresh

## Phase 2 (Feature): Manager daily digest

**Goal:** A manager gets one summary of yesterday's confirmed visits  
**One feature:** Manager daily digest  
**Why next:** The manager is the buyer, and the digest gives them a reason to pay; the cheap note apps in the case study do not offer it  
**Estimated hours:** 7

## Phase brief (paste first)

```text
The earlier phases are working. We are starting Phase 2: add ONE feature, Manager daily digest.
Goal: A manager gets one summary of yesterday's confirmed visits
Why now: The manager is the buyer, and the digest gives them a reason to pay; the cheap note apps in the case study do not offer it
Read the existing code and PROGRESS.md first. Do not rewrite or reorganise earlier features; if an earlier part must change, explain why before you change it.
Work through this phase's stages one at a time. After each stage run the tests, check that earlier features still work, and update PROGRESS.md. Stop when the stage's acceptance checks pass.
```

## Move on when

- [ ] 3 managers open the digest 3 days in a row
- [ ] Digest generation cost per team is under your budget

### Stage 2.1: Teams and roles

**Goal:** Group reps under a manager  
**You get:** teams table, manager role and an invite step  
**Estimated hours:** 3

## Prompt

```text
Add a teams table and a manager role to the existing app. A manager can see confirmed records of reps on their team and nobody else's. Do not change the rep screens. Add tests for the permission rule. Stop when the acceptance checks pass.
```

## Done when

- [ ] A manager sees only their team's confirmed records
- [ ] Reps still see only their own visits

### Stage 2.2: Digest job and email

**Goal:** Send the daily summary  
**You get:** Scheduled job that emails a summary per team  
**Estimated hours:** 4

## Prompt

```text
Add a scheduled job that, each morning, summarises yesterday's confirmed records for each team (counts, outcomes, follow-ups due) and emails it to the manager. Keep the summary template in one file. Add an unsubscribe link. Stop when the acceptance checks pass.
```

## Done when

- [ ] Digest lists yesterday's confirmed visits
- [ ] Unsubscribe works

## Phase 3 (Feature): Offline capture

**Goal:** A rep can record with no signal and have it upload later  
**One feature:** Offline capture  
**Why next:** White space in the case study: neither of the main competitors works offline, and field reps often have poor signal  
**Estimated hours:** 10

## Phase brief (paste first)

```text
The earlier phases are working. We are starting Phase 3: add ONE feature, Offline capture.
Goal: A rep can record with no signal and have it upload later
Why now: White space in the case study: neither of the main competitors works offline, and field reps often have poor signal
Read the existing code and PROGRESS.md first. Do not rewrite or reorganise earlier features; if an earlier part must change, explain why before you change it.
Work through this phase's stages one at a time. After each stage run the tests, check that earlier features still work, and update PROGRESS.md. Stop when the stage's acceptance checks pass.
```

## Move on when

- [ ] A recording made in airplane mode uploads after reconnecting with nothing lost
- [ ] 3 reps in poor-signal areas use it for a week

### Stage 3.1: Local queue

**Goal:** Store recordings on the device when offline  
**You get:** Service worker and a local queue of pending recordings  
**Estimated hours:** 5

## Prompt

```text
Make the web app installable (PWA) and add a service worker. When the upload fails because the device is offline, store the recording in IndexedDB and show it as 'waiting to upload'. Do not change the online flow. Stop when the acceptance checks pass.
```

## Done when

- [ ] An offline recording appears as waiting
- [ ] The online flow still works

### Stage 3.2: Sync and retries

**Goal:** Upload the queue when back online  
**You get:** Automatic sync with retry and no duplicates  
**Estimated hours:** 5

## Prompt

```text
When the connection returns, upload queued recordings one at a time with retry and exponential backoff. Use a client-generated id so a retried upload never creates a duplicate visit. Show sync status per recording. Add tests for the duplicate rule. Stop when the acceptance checks pass.
```

## Done when

- [ ] Interrupting a sync and retrying creates no duplicate visits
- [ ] Status shows waiting, uploading, done or failed
