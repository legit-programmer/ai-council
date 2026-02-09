# AI Council Dashboard (Next.js)

This folder contains the polished client dashboard for AI Council. The dashboard replaces the old HTML test page with a production-ready UI built on Next.js and Tailwind.

## What the dashboard does

-   Create AI Council sessions (session id, initial prompt, agent configs)
-   Connect to the FastAPI backend over WebSocket
-   Start and stop the discussion loop
-   Stream and play TTS audio in real time (24kHz int16 PCM)
-   Display live transcript updates per agent
-   Show a Zoom/Meet style call layout with active speaker highlight
-   Provide call controls: start/pause, mute toggle (visual only), end call

## Where it lives

The dashboard is in the Next.js app under:

-   apps/web/src/app/dashboard
-   apps/web/src/components/council
-   apps/web/src/hooks
-   apps/web/src/types

## Key UI pieces

-   Session setup wizard with agent cards and presets
-   Live call grid with animated agent tiles
-   Transcript panel with auto-append entries
-   Control bar with messaging, start/pause, mute, and end call

## Backend requirements

-   FastAPI server running at http://127.0.0.1:8000
-   Redis running and reachable

The dashboard uses:

-   POST /create_session
-   WS /ws/connect?session_id=...

## Environment

Set the API base URL in the Next.js app:

-   NEXT_PUBLIC_API_URL (default: http://127.0.0.1:8000)

## Run locally

From frontend/council-client:

1. pnpm install
2. pnpm dev

Open:

-   http://localhost:3001/dashboard

## Notes

-   Auth is currently disabled for the dashboard route.
-   Mute is wired to the UI only (audio input is a placeholder for now).
-   The backend audio format is int16 PCM at 24kHz, mono.
