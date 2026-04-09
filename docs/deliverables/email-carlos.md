# Draft Email — Carlos Becker

> **Instructions:**
> - Replace `[YOUR NAME]` with your name
> - Replace `[RECRUITER EMAIL]` with the recruiter's address (in cc)
> - Fill in `[WORKFLOW URL]` after publishing the HappyRobot workflow
> - Fill in `[LOOM URL]` after recording the demo video
> - Send to: **c.becker@happyrobot.ai** with recruiter in cc
> - Review and adjust tone to match your style before sending

---

**To:** c.becker@happyrobot.ai  
**Cc:** [recruiter email]  
**Subject:** Acme Logistics — Inbound Carrier Automation PoC · Ready for Review

---

Hi Carlos,

I wanted to share the latest advancements on the inbound carrier automation build ahead of our meeting.

**What's live**

The full proof-of-concept is deployed and functional:

- **Deployed API + Dashboard:** https://happyrobot-challenge-production-caf1.up.railway.app/dashboard/
- **Code repository:** https://github.com/Sekoya88/happyrobot-carrier-sales
- **HappyRobot workflow:** [WORKFLOW URL]

**What the system does**

A carrier calls in via the HappyRobot web call trigger. The AI agent:

1. Requests and verifies their MC number against the FMCSA database (with mock fallback for the demo)
2. Searches available loads by lane (origin, destination, equipment type) from a 30-lane load board
3. Pitches the best matching load with full details — rate, pickup/delivery window, commodity, weight
4. Handles up to 3 rounds of rate negotiation (ceiling capped at +5% above the posted loadboard rate)
5. On agreement, delivers a mock transfer message and records the call outcome, agreed rate, and carrier sentiment

**Dashboard highlights**

The broker-facing dashboard (built custom, not platform analytics) shows:
- Conversion rate, revenue, avg/best agreed rate, avg call duration
- Today vs. yesterday call volume delta
- 7-day call + booking trend line
- Full call record table with search and outcome filters

**5-min demo walkthrough:** [LOOM URL]

I've also prepared a full build description document for Acme Logistics that covers the architecture, integration requirements, and deployment steps — happy to walk through it on the call.

Looking forward to our conversation.

Best,  
[YOUR NAME]
