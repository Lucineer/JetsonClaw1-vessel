# Fleet Health Audit

**Date:** 2026-04-03 01:21 AKDT  
**Base URL:** `https://<repo>.magnus-digennaro.workers.dev`

## Summary

- **Total repos checked:** 27
- **All-green (200/200/200):** 4 (deckboss-ai, businesslog-ai, cocapn, cocapn-lite)
- **Healthy but /api/efficiency missing or erroring:** 18
- **Not deployed (404 on all endpoints):** 6
- **Broken (500 on all endpoints):** 3

## Full Results

| Repo | /health | /setup | /api/efficiency | Notes |
|------|---------|--------|-----------------|-------|
| cocapn | 200 | 200 | 200 | ✅ All green |
| cocapn-lite | 200 | 200 | 404 | /api/efficiency not implemented |
| deckboss-ai | 200 | 200 | 200 | ✅ All green |
| businesslog-ai | 200 | 200 | 200 | ✅ All green |
| dmlog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| makerlog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| personallog-ai | 200 | 200 | 500 | **BUG:** `Cannot read properties of undefined (reading 'get')` |
| studylog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| fishinglog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| luciddreamer-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| reallog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| playerlog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| activelog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| activeledger-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| travlog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| healthlog-ai | 200 | 200 | 404 | /api/efficiency not implemented |
| nightlog-ai | 500 | 500 | 500 | **BROKEN:** Worker error 1101 |
| podcast-ai | 500 | 500 | 500 | **BROKEN:** Worker error 1101 |
| mycelium-ai | 500 | 500 | 500 | **BROKEN:** Worker error 1101 |
| cooklog-ai | 404 | 404 | 404 | ⚠️ Serves HTML at / but no API routes |
| booklog-ai | 404 | 404 | 404 | ⚠️ Worker error 1101 (not deployed?) |
| petlog-ai | 404 | 404 | 404 | ⚠️ Worker error 1042 (not deployed?) |
| gardenlog-ai | 404 | 404 | 404 | ⚠️ Serves HTML at / but no API routes |
| kungfu-ai | 404 | 404 | 404 | ⚠️ Serves HTML at / but no API routes |
| sciencelog-ai | 404 | 404 | 404 | ⚠️ Serves HTML at / but no API routes |
| craftlog-ai | 404 | 404 | 404 | ⚠️ Returns `[object Response]` at / (broken worker) |
| travelog-ai | 404 | 404 | 404 | ⚠️ Worker error 1042 (not deployed?) |

## Issues to Address

### 🔴 Critical (500 errors — workers crashing)
- **nightlog-ai, podcast-ai, mycelium-ai** — Cloudflare Worker error 1101 on all endpoints. Workers likely need redeployment or bindings are missing.

### 🟡 Medium (404 on all endpoints — partially deployed)
- **booklog-ai, petlog-ai, travelog-ai** — Worker errors 1101/1042 suggest workers exist but are misconfigured or undeployed.
- **cooklog-ai, gardenlog-ai, kungfu-ai, sciencelog-ai** — Serve static HTML frontend at `/` but have no API routes deployed (no /health, /setup, etc).
- **craftlog-ai** — Worker returns `[object Response]` (serialization bug in the worker).

### 🟢 Low (functionality gaps)
- **personallog-ai** — /api/efficiency throws 500 (`Cannot read properties of undefined (reading 'get')`). Likely a missing binding/env var.
- **18 repos** — /api/efficiency returns 404. Route likely not yet implemented in these workers.
