# HappyRobot — Inbound Carrier Sales Automation

Proof-of-concept backend for automating inbound carrier calls. Carriers call in, get verified via FMCSA, matched to a load, and negotiate pricing — all handled by an AI voice agent on the HappyRobot platform backed by this API.

## Architecture

```
HappyRobot Voice Agent  →  FastAPI Backend  →  SQLite
(conversation layer)       (business logic)    (call history)
                                ↓
                         /dashboard (broker KPIs)
```

- **HappyRobot**: inbound voice agent, tool calls, conversation flow
- **FastAPI**: carrier verification, load search, negotiation rules, call recording, metrics
- **SQLite**: call history (swappable to Postgres behind the repository layer)
- **Dashboard**: custom broker KPI UI (not HappyRobot analytics) — Aurora-style minimal UI at `/dashboard/`; static assets under `/dashboard/dashboard.css`. The HTML shell is rendered by FastAPI so `API_KEY` is injected from the server environment (source file on disk still contains a placeholder for local inspection only).

## Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | /health | None | Health check |
| GET | /verify-carrier/{mc_number} | x-api-key | FMCSA carrier verification |
| GET | /loads | x-api-key | Search loads (origin, destination, equipment_type) |
| GET | /loads/{load_id} | x-api-key | Get load by ID |
| POST | /calls | x-api-key | Record call outcome |
| GET | /metrics | x-api-key | Broker KPI metrics |
| GET | /dashboard/ | None | Broker dashboard UI (injects API key into page) |
| GET | /dashboard/dashboard.css | None | Dashboard stylesheet |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| API_KEY | Yes | API key for all protected endpoints |
| FMCSA_API_KEY | Yes | FMCSA web service key |
| FMCSA_MOCK_FALLBACK | No | Set `true` to use mock data (default: true) |
| LOADS_FILE | No | Path to loads JSON (default: data/loads.json) |

## Local Development

```bash
cp .env.example .env
# Edit .env with your keys
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Test: `curl http://localhost:8000/health`

Dashboard: `open http://localhost:8000/dashboard/`

Metrics (example): `curl -s -H "x-api-key: $API_KEY" http://localhost:8000/metrics | head -c 400`

## Docker

```bash
docker compose up --build
```

## Tests

```bash
pytest tests/ -v
```

Tests: negotiation, load search, metrics, FMCSA/MC validation, dashboard contract + served HTML.

## Deliverables

- **Workflow**: https://platform.happyrobot.ai/workflows/[WORKFLOW_SLUG]
- **Dashboard**: https://[RAILWAY_URL]/dashboard
- **Repository**: https://github.com/[USERNAME]/happyrobot-challenge
- **Demo video**: https://loom.com/[VIDEO_ID]

## Demo Script

| Step | Carrier says | Agent does |
|------|-------------|------------|
| Start | "Hi, I need a load" | Greet, ask MC number |
| MC | "123456" | Call verify_carrier → eligible |
| Lane | "Chicago to Dallas, Dry Van" | Call search_loads → present LD-001 ($3,000) |
| Rate | "Can you do $3,100?" | Accept (within 5% ceiling of $3,150) |
| Close | "Sounds good" | Transfer message + record_call(booked) |

## Negotiation Rules

- Max 3 counter-offer rounds
- Ceiling: +5% above loadboard rate
- Progressive counter-offers toward ceiling
- Outcomes: `booked` / `no_deal` / `abandoned`
