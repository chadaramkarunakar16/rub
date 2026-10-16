# Backend patterns by feature type

Starting points for the "How does it work?" and "The stack" sections. Each entry gives the
core problem, the common approaches, and a default stack for a solo builder or small team.
Always confirm specifics for a named product from public sources before attributing them.

## Realtime presence and live cursors (Figma, Google Docs style)
- **Core problem:** many clients need to see each other's state within ~100 ms.
- **Approaches:** WebSocket server broadcasting ephemeral state; managed realtime service;
  peer-to-peer (WebRTC) for small rooms.
- **Key ideas:** ephemeral vs durable state, throttling (send cursor updates ~20/s), rooms/channels,
  reconnect handling.
- **Default stack:** Next.js + a realtime service (Supabase Realtime, Liveblocks, PartyKit) or
  a Node `ws` server; Redis pub/sub when scaling past one server.

## Collaborative editing (Notion, Google Docs style)
- **Core problem:** two people edit the same text at once without losing either change.
- **Approaches:** Operational Transformation (OT, central server orders edits) vs CRDTs
  (edits merge automatically, works offline).
- **Key ideas:** document model (blocks vs plain text), conflict resolution, persistence of updates,
  undo history.
- **Default stack:** Yjs (CRDT) + y-websocket or Hocuspocus, TipTap/ProseMirror editor, Postgres for snapshots.

## Infinite feed (Instagram, X, YouTube Shorts style)
- **Core problem:** serve a fresh, ranked, endless list fast.
- **Approaches:** fan-out on write (precompute each user's feed) vs fan-out on read (assemble on request);
  hybrid for accounts with huge followings.
- **Key ideas:** cursor-based pagination (not page numbers), caching, ranking signals, prefetching.
- **Default stack:** Postgres with keyset pagination, Redis for hot feeds, a CDN for media,
  React Query / TanStack Query on the client.

## Full-text and semantic search (Notion search, Algolia style)
- **Core problem:** return relevant results in under ~100 ms as the user types.
- **Approaches:** inverted index (keyword), vector embeddings (meaning), hybrid of both.
- **Key ideas:** tokenisation, ranking (BM25), typo tolerance, debouncing input, embeddings + similarity.
- **Default stack:** Postgres full-text + pgvector to start; Meilisearch or Typesense when it grows.

## AI chat with memory (ChatGPT, Claude style)
- **Core problem:** stream answers token by token and remember useful context across chats.
- **Approaches:** full history in the prompt; summarised history; retrieval (RAG) over stored memories.
- **Key ideas:** streaming (SSE), context windows, embeddings, tool calling, rate limits and cost control.
- **Default stack:** Next.js + Vercel AI SDK or the provider SDK, Postgres + pgvector for memory,
  a queue for long jobs.

## Payments with retries (Stripe, Razorpay checkout style)
- **Core problem:** never charge twice and never lose a payment, even when networks fail.
- **Approaches:** hosted checkout vs embedded; webhooks as the source of truth.
- **Key ideas:** idempotency keys, webhook signature verification, payment state machine, reconciliation.
- **Default stack:** Razorpay (India) or Stripe, a webhook endpoint, a `payments` table with status history.

## Short-video upload and playback (Reels, TikTok style)
- **Core problem:** upload large files reliably and play them instantly on any network.
- **Approaches:** direct-to-storage uploads; transcoding into multiple bitrates; adaptive streaming (HLS).
- **Key ideas:** presigned URLs, resumable uploads, transcoding queue, CDN, thumbnails.
- **Default stack:** S3-compatible storage (Cloudflare R2), Mux or Cloudflare Stream for transcoding and
  playback, or FFmpeg workers if self-hosting.

## Notifications (push, email, in-app)
- **Core problem:** deliver the right message once, on the right channel, at the right time.
- **Approaches:** direct sends vs an event bus with a notification service.
- **Key ideas:** queues, retries with backoff, user preferences, deduplication, digesting.
- **Default stack:** a job queue (BullMQ, Inngest, or Supabase queues), FCM for push, Resend for email.

## Auth and accounts
- **Core problem:** prove who someone is and keep them safely signed in.
- **Approaches:** sessions vs JWTs; managed auth vs self-built.
- **Key ideas:** password hashing, OAuth, magic links, refresh tokens, role-based access, row-level security.
- **Default stack:** Supabase Auth, Clerk, or Auth.js.
