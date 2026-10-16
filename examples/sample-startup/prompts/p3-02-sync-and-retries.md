# Stage 3.2: Sync and retries

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
