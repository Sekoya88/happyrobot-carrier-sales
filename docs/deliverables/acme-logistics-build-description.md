# Inbound Carrier Automation — Build Description

**Client:** Acme Logistics  
**Prepared by:** [YOUR NAME]  
**Date:** April 2026  
**Version:** 1.0  

---

## Executive Summary

This document describes the proof-of-concept inbound carrier sales automation built for Acme Logistics. The system replaces manual inbound carrier calls with an AI voice agent that verifies carriers, matches them to available loads, negotiates rates within defined parameters, and records every interaction for broker review — all without human intervention.

---

## Business Problem

Freight brokers spend significant time fielding inbound carrier calls that follow a predictable, repetitive pattern: verify eligibility, find a matching load, negotiate a rate. This is high-volume, low-differentiation work that keeps sales reps away from strategic activities.

**This system automates the full inbound carrier call cycle** — from first hello to call outcome recording — and surfaces performance data on a live broker dashboard.

---

## Solution Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        HappyRobot Platform                      │
│  ┌───────────────┐    tool calls     ┌──────────────────────┐  │
│  │  AI Voice     │ ◄────────────────► │  FastAPI Backend     │  │
│  │  Agent        │                   │  (Railway, Docker)   │  │
│  │  (web call    │   POST /calls      │                      │  │
│  │   trigger)    │ ─────────────────► │  - verify_carrier    │  │
│  └───────────────┘                   │  - search_loads      │  │
│                                      │  - record call       │  │
│                                      │  - metrics API       │  │
│                                      └──────────┬───────────┘  │
└────────────────────────────────────────────────┼────────────────┘
                                                 │
                                          ┌──────┴──────┐
                                          │   SQLite DB  │
                                          │ (call history│
                                          └──────┬───────┘
                                                 │
                                         ┌───────┴────────┐
                                         │  /dashboard/   │
                                         │  (Broker KPIs) │
                                         └────────────────┘
```

**Components:**

| Layer | Technology | Purpose |
|-------|------------|---------|
| Voice agent | HappyRobot (web call trigger) | Conversational AI, tool calls, sentiment extraction |
| Backend API | Python / FastAPI | Carrier verification, load search, negotiation logic, call recording |
| Database | SQLite | Persistent call history (swappable to PostgreSQL) |
| Dashboard | HTML + Chart.js | Real-time broker KPI reporting |
| Deployment | Docker + Railway | Cloud hosting, HTTPS, CI/CD via GitHub |

---

## Core Capabilities

### 1. Carrier Eligibility Verification

When a carrier calls, the agent captures their MC number and immediately verifies eligibility against the **FMCSA database** (the authoritative US federal carrier registry).

- MC numbers are validated client-side before the API call: digits only, 6–8 characters
- Non-numeric or malformed MC numbers are rejected immediately with a clear carrier message
- The system returns: carrier name, DOT number, eligibility status, active/inactive flag
- Demo mode uses a deterministic mock that mirrors real FMCSA response shapes

### 2. Load Search & Pitch

The agent searches the load board using the carrier's stated lane (origin, destination) and equipment type.

**Load board fields:**

| Field | Description |
|-------|-------------|
| Load ID | Unique reference (e.g. `LD-001`) |
| Origin → Destination | Lane |
| Pickup / Delivery | Date + time windows |
| Equipment type | Dry Van, Reefer, Flatbed |
| Loadboard rate | Posted rate ($) |
| Weight | Lbs |
| Commodity | Type of goods |
| Miles | Transit distance |
| Notes | Special requirements |

The agent pitches the best match with full details — rate, timing, commodity, weight, and any special notes (e.g. "Temperature controlled -10F", "Oversize permit on file").

### 3. Automated Rate Negotiation

If the carrier counter-offers, the agent negotiates within defined parameters:

- **Ceiling:** posted `loadboard_rate × 1.05` (5% above market)
- **Rounds:** maximum 3 exchanges per call
- **Strategy:** progressive counter-offers stepping toward the ceiling
- **On agreement:** agent delivers a mock transfer message — *"Transfer was successful. You can now wrap up the conversation."*
- **On refusal (3 rounds exceeded or carrier declines):** call ends with `no_deal` outcome

### 4. Call Outcome Recording

At the end of every call, an AI Extract node in the HappyRobot workflow captures structured data, which is persisted to the backend via `POST /calls`:

| Field | Description |
|-------|-------------|
| MC number | Verified carrier identifier |
| Load ID | The load discussed |
| Outcome | `booked`, `no_deal`, or `abandoned` |
| Sentiment | `positive`, `neutral`, or `negative` |
| Agreed rate | Final accepted rate (booked calls only) |
| Negotiation rounds | How many back-and-forths occurred |
| Call duration | Total call length in seconds |

---

## Broker Dashboard

The dashboard is custom-built — not the HappyRobot platform analytics. It connects to the backend metrics API and refreshes in real time.

**Access:** https://happyrobot-challenge-production-caf1.up.railway.app/dashboard/

### KPIs

| Metric | How it's calculated |
|--------|---------------------|
| Conversion rate | `booked / total_calls` — displayed as hero stat |
| Total calls | Volume + delta badge vs. yesterday |
| Booked / No deal / Abandoned | Outcome breakdown |
| Revenue | Sum of all agreed rates on booked calls |
| Avg rate | Mean agreed rate on booked calls |
| Best rate | Highest single agreed rate |
| Avg call duration | Mean call length across all calls |

### Charts

- **Outcome donut** — Booked / No deal / Abandoned distribution
- **Sentiment donut** — Positive / Neutral / Negative carrier sentiment
- **7-day trend line** — Total calls + bookings per day

### Call Records Table

Full searchable, sortable table of all calls with MC number, load, outcome, sentiment, rate, negotiation rounds, duration, and timestamp. Filterable by outcome. Export to CSV.

---

## Security

| Requirement | Implementation |
|-------------|----------------|
| HTTPS | Railway edge TLS — all traffic TLS 1.2+ terminated before container |
| API authentication | `x-api-key` header required on all API endpoints |
| Dashboard key | Injected server-side at request time — never in source code |
| Container security | Non-root user (`appuser`), minimal base image (`python:3.11-slim`) |
| MC validation | Input sanitized before any external API call |

---

## Deployment

The system is containerized with Docker and deployed to Railway (cloud PaaS).

### Access

| Resource | URL |
|----------|-----|
| Dashboard | https://happyrobot-challenge-production-caf1.up.railway.app/dashboard/ |
| Health check | https://happyrobot-challenge-production-caf1.up.railway.app/health |
| API docs | https://happyrobot-challenge-production-caf1.up.railway.app/docs |

### Reproduce the deployment

1. Clone https://github.com/Sekoya88/happyrobot-carrier-sales
2. Create a Railway project → Deploy from GitHub repo
3. Set environment variables:

| Variable | Value |
|----------|-------|
| `API_KEY` | strong secret (e.g. `openssl rand -hex 16`) |
| `FMCSA_API_KEY` | FMCSA web services key |
| `FMCSA_MOCK_FALLBACK` | `true` for demo, `false` for live FMCSA |

4. Railway auto-detects the `Dockerfile` and deploys. No additional configuration needed.

### Local Docker

```bash
cp .env.example .env   # fill in keys
docker compose up --build
open http://localhost:8000/dashboard/
```

---

## HappyRobot Workflow Integration

The HappyRobot agent is configured with:

- **Inbound web call trigger** (no phone number purchased)
- **Two tool calls:**
  - `verify_carrier(mc_number)` → `GET /verify-carrier/{mc_number}`
  - `search_loads(origin, destination, equipment_type)` → `GET /loads`
- **AI Extract node** at call end → captures outcome, sentiment, agreed rate, negotiation count, duration
- **Webhook** → `POST /calls` with the extracted structured data

**Workflow link:** [PASTE HAPPYROBOT WORKFLOW URL]

---

## Test Coverage

26 automated tests covering:

- Negotiation rules (ceiling enforcement, round limits, outcome mapping)
- Load search (origin/destination/equipment filters)
- Metrics computation (conversion, revenue, avg rate, calls today/yesterday)
- MC number validation (format, normalization, edge cases)
- FMCSA client (eligible, ineligible, invalid format)
- Dashboard contract (API key injection, XSS-safe DOM, required hooks)

---

## Limitations & Next Steps

| Item | Current state | Production path |
|------|--------------|-----------------|
| Load database | Static JSON (30 lanes) | Connect to live TMS / load board API |
| FMCSA integration | Mock fallback | Enable `FMCSA_MOCK_FALLBACK=false` with a real FMCSA API key |
| Persistence | SQLite | Swap to PostgreSQL (repository pattern already in place) |
| Transfer | Mock message | Integrate real SIP transfer or CRM handoff |
| Auth | API key | Upgrade to OAuth2 / short-lived tokens for production |
| Call recording | Structured fields | Add audio recording link field if HappyRobot exposes it |
