# Stage 3.1: Local queue

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
