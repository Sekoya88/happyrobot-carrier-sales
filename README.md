# HappyRobot — Inbound Carrier Sales Automation

Proof-of-concept backend for automating inbound carrier calls for a freight brokerage. Carriers call in, get verified via FMCSA, are matched to a load, and negotiate pricing — all handled by an AI voice agent on the HappyRobot platform backed by this FastAPI service.

---

## Architecture

```
HappyRobot Voice Agent  ──tool calls──►  FastAPI Backend  ──►  SQLite
(conversation + NLP)                     (business logic)       (call history)
                                               │
                                         /dashboard/
                                       (broker KPI UI)
```

- **HappyRobot**: inbound web-call agent, `verify_carrier` + `search_loads` tool calls, AI Extract node for call data, conversation flow
- **FastAPI**: carrier verification, load search, negotiation rules, call recording, metrics API
- **SQLite**: persistent call history (repository pattern — swap to Postgres without touching domain code)
- **Dashboard**: custom Aurora-style broker KPI UI at `/dashboard/`; API key injected server-side by FastAPI

---

## Objective 1 — Inbound Use Case

### Call Flow

```
Carrier calls in (web call trigger)
  → Agent asks for MC number
  → verify_carrier(mc_number)     # FMCSA eligibility check
  → If ineligible → politely end call
  → Agent asks for lane + equipment type
  → search_loads(origin, destination, equipment_type)
  → Agent pitches load details (rate, pickup, delivery, commodity)
  → Negotiation loop (max 3 rounds, ceiling = loadboard_rate × 1.05)
  → If price agreed → mock transfer message → AI Extract → POST /calls
  → If no deal / abandoned → AI Extract → POST /calls
```

### Carrier Verification

`GET /verify-carrier/{mc_number}` — calls FMCSA web services (mock fallback enabled by default). Returns:

```json
{
  "mc_number": "123456",
  "eligible": true,
  "status": "ACTIVE",
  "dot_number": "1234567",
  "legal_name": "FAST FREIGHT LLC"
}
```

MC numbers are validated before hitting FMCSA: digits-only, 6–8 digits. Non-numeric or short MCs return `eligible: false, status: INVALID_MC_FORMAT` immediately.

### Load Data

Loads are stored in `data/loads.json` (30 lanes, searchable by origin / destination / equipment type).

| Field | Type | Description |
|-------|------|-------------|
| `load_id` | string | Unique identifier (e.g. `LD-001`) |
| `origin` | string | Starting location |
| `destination` | string | Delivery location |
| `pickup_datetime` | ISO 8601 | Date and time for pickup |
| `delivery_datetime` | ISO 8601 | Date and time for delivery |
| `equipment_type` | string | `Dry Van`, `Reefer`, `Flatbed` |
| `loadboard_rate` | float | Listed rate ($) |
| `notes` | string | Additional information |
| `weight` | float | Load weight (lbs) |
| `commodity_type` | string | Type of goods |
| `num_of_pieces` | int | Number of items |
| `miles` | float | Distance to travel |
| `dimensions` | string | Size measurements (e.g. `48x102`) |

### Negotiation Rules

- **Ceiling**: `loadboard_rate × 1.05` (5% above listed rate)
- **Max rounds**: 3 counter-offer exchanges
- **Strategy**: progressive counter-offers toward the ceiling
- **Outcomes**: `booked` / `no_deal` / `abandoned`
- **Transfer**: on booking, agent delivers mock transfer message: *"Transfer was successful — you can now wrap up the conversation."*

---

## Objective 2 — Metrics Dashboard

Custom broker KPI dashboard at `/dashboard/` (not HappyRobot platform analytics).

**Live:** https://happyrobot-challenge-production-caf1.up.railway.app/dashboard/

### KPIs displayed

| Metric | Description |
|--------|-------------|
| Conversion rate | `booked / total_calls` — hero stat |
| Total calls | Count + today vs yesterday delta badge |
| Booked | Successful bookings |
| No deal | Negotiations that didn't close |
| Revenue | Sum of agreed rates on booked calls |
| Avg rate | Mean agreed rate on booked calls |
| Best rate | Highest agreed rate ever |
| Avg call duration | Mean `duration_seconds` across all calls |

Charts: outcome donut, sentiment donut, 7-day call + booking line chart.

### Metrics API

```bash
curl -H "x-api-key: $API_KEY" https://happyrobot-challenge-production-caf1.up.railway.app/metrics
```

---

## Objective 3 — Deployment & Infrastructure

### Docker (Containerized)

```bash
cp .env.example .env   # fill in API_KEY and FMCSA_API_KEY
docker compose up --build
open http://localhost:8000/dashboard/
```

The `Dockerfile` uses `python:3.11-slim`, runs as a non-root user (`appuser`), and exposes port `$PORT` (injected by Railway).

---

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | Health check |
| GET | `/verify-carrier/{mc_number}` | x-api-key | FMCSA carrier verification |
| GET | `/loads` | x-api-key | Search loads (origin, destination, equipment_type) |
| GET | `/loads/{load_id}` | x-api-key | Get load by ID |
| POST | `/calls` | x-api-key | Record call outcome |
| GET | `/metrics` | x-api-key | Broker KPI metrics |
| GET | `/dashboard/` | None | Broker dashboard UI (API key injected server-side) |

---

## Security

All endpoints except `/health` and `/dashboard/` require `x-api-key` header matching `API_KEY` env var.

The dashboard API key is **injected server-side** — it never appears in the versioned source file. The on-disk HTML contains a literal placeholder (`__API_KEY_JSON__`) replaced at request time by `serve_dashboard()` in `app/main.py`.

HTTPS is enforced by Railway's edge proxy. All `*.up.railway.app` traffic is TLS-terminated before reaching the container.

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_KEY` | Yes | API key for all protected endpoints |
| `FMCSA_API_KEY` | Yes | FMCSA web service key |
| `FMCSA_MOCK_FALLBACK` | No | `true` to use mock data (default: `true`) |
| `LOADS_FILE` | No | Path to loads JSON (default: `data/loads.json`) |

---

## Local Development

```bash
cp .env.example .env
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```bash
curl http://localhost:8000/health
open http://localhost:8000/dashboard/
curl -s -H "x-api-key: $API_KEY" http://localhost:8000/metrics
```

---

## Deployment Reproduction (Railway)

Live deployment: `https://happyrobot-challenge-production-caf1.up.railway.app`

### Re-deploy from scratch

1. Fork / clone this repository
2. Create a new Railway project → **Deploy from GitHub repo** → select this repo
3. Set environment variables in Railway → **Settings → Variables**:

| Variable | Value |
|----------|-------|
| `API_KEY` | strong secret — e.g. `openssl rand -hex 16` |
| `FMCSA_API_KEY` | your FMCSA web services key |
| `FMCSA_MOCK_FALLBACK` | `true` (demo) or `false` (live FMCSA) |

4. Railway auto-detects the `Dockerfile`. `PORT` is injected automatically.
5. Access at `https://<your-railway-domain>/dashboard/`

---

## Tests

```bash
pytest tests/ -v
```

26 tests: negotiation rules, load search, metrics (incl. new KPIs), FMCSA/MC validation, dashboard contract + server-side API key injection.

---

## Demo Script

| Step | Carrier says | Agent does |
|------|-------------|------------|
| 1 | "Hi, I'm looking for a load" | Greet, ask for MC number |
| 2 | "My MC is 123456" | Call `verify_carrier` → eligible |
| 3 | "Chicago to Dallas, Dry Van" | Call `search_loads` → present LD-001 at $3,000 |
| 4 | "Can you do $3,100?" | Evaluate → within 5% ceiling ($3,150) → accept |
| 5 | "Deal" | Mock transfer message → AI Extract → `POST /calls` (booked) |

---

## Deliverables

| # | Deliverable | Status | Link |
|---|-------------|--------|------|
| 1 | Email to Carlos Becker | ✏️ to send | `docs/deliverables/email-carlos.md` |
| 2 | Acme Logistics build description | ✅ drafted | `docs/deliverables/acme-logistics-build-description.md` |
| 3 | Deployed dashboard | ✅ live | https://happyrobot-challenge-production-caf1.up.railway.app/dashboard/ |
| 4 | Code repository | ✅ | https://github.com/Sekoya88/happyrobot-carrier-sales |
| 5 | HappyRobot workflow link | ✏️ to publish | [paste URL after publishing workflow] |
| 6 | Demo video (5 min) | ✏️ to record | [paste Loom URL after recording] |
