# Acme Logistics — Inbound Carrier Sales Automation

## Executive Summary

This proof of concept automates the qualification and booking of inbound carrier calls. When a carrier calls in, an AI voice agent handles the entire interaction: verifying the carrier's credentials, presenting a matching load, and negotiating the rate — without requiring a human broker to be on the line.

## How It Works

1. **Carrier calls in** via the web call link
2. **Agent asks for MC number** and verifies eligibility against the FMCSA database
3. **Agent searches for a matching load** based on the carrier's lane (origin, destination, equipment type)
4. **Agent pitches the load** with rate, pickup date, and commodity details
5. **Negotiation**: up to 3 counter-offer rounds; the agent never exceeds 5% above the listed rate
6. **If a deal is reached**: the agent confirms the booking and hands off to a sales rep
7. **All calls are recorded**: outcome, sentiment, agreed rate, and number of negotiation rounds

## Business Benefits

| Benefit | Detail |
|---------|--------|
| 24/7 availability | Carriers can call at any time without waiting for a rep |
| Consistent pricing discipline | Agent never exceeds the authorized rate ceiling |
| Faster qualification | FMCSA verification happens in seconds |
| Full visibility | Every call is logged with outcome and sentiment data |
| Broker dashboard | Real-time KPIs: conversion rate, outcome breakdown, sentiment trends |

## Performance Metrics (Dashboard)

The broker dashboard shows:
- **Total calls** handled by the agent
- **Booked vs. No Deal vs. Abandoned** breakdown
- **Conversion rate** (booked / total)
- **Sentiment breakdown** (positive / neutral / negative)
- **Recent call log** with rate and negotiation rounds

## Proof of Concept Scope

This PoC covers the core qualification and negotiation flow. Production hardening would add:
- Persistent database (PostgreSQL)
- Full authentication and audit logging
- Integration with TMS/load board systems
- Retry logic and voicemail handling
- Richer analytics and alerting

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Voice agent | HappyRobot platform |
| API | FastAPI (Python) |
| Carrier verification | FMCSA API |
| Data storage | SQLite (PoC) → PostgreSQL (production) |
| Deployment | Docker + Railway |
| Dashboard | Single-page web app |
