# Current Platform Versions

## Home Assistant 2026.4
- **IR Proxy** — Native infrared entity platform. ESPHome devices with IR transmitter expose `InfraredEntity`. HA sends commands through them. First integration: LG Infrared (LG TVs). → Route to **Volt** + **Sage**
- **Cross-domain automation triggers** — More intuitive triggers aligned to how users think (in Labs). → Route to **Sage**
- **Matter lock PIN management** — Full PIN code control for Matter locks. → Route to **Sage** or **Nano**
- **Dashboard: section background colors** — Sections can now have background colors. → Route to **Iris**
- **Dashboard: card favorites** — Pin favorite entities to cards. → Route to **Iris**
- **AI Assist transparency** — Visual indicator of what Assist is processing. → Route to **Mira**
- **Voice: vacuum area cleaning** — Ask Assist to clean a specific area. → Route to **Echo**
- **New integrations** — UniFi Access, WiiM, Solarman, TRMNL (e-paper display). → Route to **Grid** (UniFi), **Ada** (others)
- **Backup upload progress** — Per-location upload percentage visible. → Route to **Forge**

## ESPHome 2026.3
- **IR/RF Proxy** (`ir_rf_proxy`) — Runtime IR/RF signal transmission without reflashing. Learns and replays commands. Works with `remote_transmitter` / `remote_receiver`. → Route to **Volt**
- **RP2040 / RP2350 first-class support** — pico-sdk 2.0, 143+ board definitions, BLE foundations, crash diagnostics. → Route to **Volt**
- **Media player redesign** — Pluggable sources, playlists, Ogg Opus support. → Route to **Echo**
- **Performance** — Main loop up to 99x faster, API protobuf 6–12x faster, 11–20KB flash savings. No config changes needed — just reflash.
- **ESP8266 heap crash fix** — Long-standing LWIP use-after-free bug resolved.
