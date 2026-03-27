---
description: Connect external APIs to Home Assistant - Tibber, SMHI, SL, OpenAI, Spotify, Telegram, Shelly, Hue, and more
---

**Why ask first:** API integrations vary by target platform (Node-RED vs HA YAML vs Python integration),
authentication needs, and what data the user actually wants. A few quick questions save significant rework.

## First Response

Ask these questions BEFORE generating any code:

1. **API/Service:** Which API or service do you want to connect? (e.g., Tibber, SMHI, Telegram)
2. **Platform:** Node-RED flow, HA YAML REST sensor, or full Python integration?
3. **Goal:** What data or action do you need? (e.g., current electricity price, send notifications)
4. **Credentials:** Do you already have an API key/token?

**Example correct response:**
> I'll help you connect Tibber to Home Assistant. Let me clarify:
> 1. Do you want a Node-RED flow or a YAML REST sensor?
> 2. What data - current price only, or also today's hourly prices?
> 3. Do you have a Tibber Personal Access Token from developer.tibber.com?

THEN STOP. Wait for answers.

---

**What this does:**
- Provides working connection code for 20+ popular APIs
- Covers energy (Tibber, Nordpool), weather (SMHI, OWM, yr.no), transport (SL, Trafikverket, Resrobot, Entur)
- Smart home clouds (Shelly, Tuya, Philips Hue, IKEA Dirigera)
- Global APIs (OpenAI, Spotify, Google Calendar, Telegram, GitHub)
- Always puts credentials in `!secret` / env vars - never hardcoded
