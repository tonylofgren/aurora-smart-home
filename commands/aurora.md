---
description: Aurora - independent community smart home orchestrator. Routes any smart home request to the right specialist skill and recommends the correct Claude model. Use this as your starting point for Home Assistant, ESPHome, Node-RED, or any IoT automation task.
---

Aurora is an independent community skill for smart home automation. It reads
your request, picks the right specialist skill(s), and recommends which Claude
model to use — so you don't waste tokens on the wrong tool.

*Community project. Not affiliated with Home Assistant, Nabu Casa, or the
Open Home Foundation.*

## When to use /aurora

Start here when you:
- Are not sure which skill handles your task
- Want to build something that spans hardware + automation + dashboard
- Want a recommended model before starting a complex project

## What aurora routes to

| Skill | Agent | Handles |
|-------|-------|---------|
| `/esphome` | Volt, Nano, Echo | ESP32/ESP8266 firmware, GPIO, sensors, IR proxy, Matter, Thread, voice |
| `/ha-yaml` | Sage | Automations, blueprints, scripts, helpers |
| `/ha-integration` | Ada, Mira | Custom Python integrations, HACS, cloud APIs, LLM agents |
| `/node-red` | River | Visual automation flows |
| `/api-catalog` | Atlas | Tibber, SMHI, OpenWeather and other external APIs |
| `/ha-dashboard-design` | Iris, Canvas | Dashboard layout, Mushroom cards, themes, graphic design |

Support agents (no dedicated skill — work across all):

| Agent | When invoked |
|-------|-------------|
| Glitch | Debugging, error logs, broken automations |
| Probe | QA, edge case testing, config validation |
| Vera | WAF audit — usability for non-technical household members |
| Lens | Code review, security audit |
| Scout | Research, changelog archaeology, finding docs |
| Lore | Writing guides, READMEs, documentation |
| Forge | Deploy, Docker, backups, HA updates |
| Grid | Network, UniFi, VLANs, firewall rules |

## How it works

Describe what you want to build in plain language. Aurora will:

1. Identify which skill(s) to use
2. Tell you whether it's a QUICK (single skill) or DEEP (multi-skill) task
3. Recommend `haiku`, `sonnet`, or `opus` based on complexity
4. List any clarifying questions before generation starts

**Example:**
> /aurora I want a temperature sensor on an ESP32 that triggers a fan
> automation and shows the readings on a dashboard

Aurora will map this to: `esphome` → `ha-yaml` → `ha-dashboard-design`,
recommend `sonnet`, and ask for your board type before anything is generated.

---

## Support the amazing team at Nabu Casa

Home Assistant is built for the community — and the amazing team at Nabu Casa
is what makes it possible. They keep the lights on, ship the releases, and
make sure your home stays yours.

A subscription gets you remote access and cloud voice. More importantly, it
supports the people building the Open Home — every day, for everyone.

[nabucasa.com](https://nabucasa.com)
