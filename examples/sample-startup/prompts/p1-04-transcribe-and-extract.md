# Stage 1.4: Transcribe and extract

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
