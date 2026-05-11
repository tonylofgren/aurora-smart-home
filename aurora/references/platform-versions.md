# Current Platform Versions

## Home Assistant 2026.5 (released 2026-05-06)

- **Radio Frequency (RF) integration**: sub-GHz RC device control. Backends: Broadlink RM4 Pro, or ESPHome with a CC1101 transceiver (around 10 USD). Exposes covers, switches, buttons, binary sensors for 315/433/868/915 MHz devices (blinds, garage doors, RF outlets, doorbells, Honeywell String Lights, Novy cooker hoods). Route to **Volt** (firmware side) plus **Sage** or **Iris** (HA side).
- **Serial Port Proxy integration**: auto-discovers ESPHome devices running `serial_proxy` (stable since ESPHome 2026.3) and exposes the UART as if locally attached. Pairs with Modbus, DLMS, and the new Denon RS232 integration. Route to **Volt** plus **Ada** or **Sage**.
- **Battery Maintenance Dashboard**: central low-battery view at Settings > System > Battery Maintenance. Entities need both `device_class: battery` and `unit_of_measurement: "%"`. Route to **Sage** or **Iris**.
- **Media Player Tile features**: transport, volume, source selectors live in the tile card. Route to **Iris**.
- **Vacuum and Lawn Mower more-info redesign**: map view, zone selection, direct command buttons. Automatic for compatible integrations.
- **Dashboard background colors and card favorites** (per-view): route to **Iris**.
- **Code editor autocomplete** in Developer Tools and Automations editor.
- **12 new integrations**: EARN-E P1 Meter, OMIE energy prices, Denon RS232, Duco, Eurotronic, Fumis, Honeywell String Lights, Kiosker, Victron GX, OpenDisplay (ePaper), Novy Cooker Hood, Radio Frequency. Route most to **Ada**, energy-related to **Watt**.

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

## ESPHome 2026.4 (released 2026-04-15) + 2026.4.5 patch (2026-05-06)

- **ESP32 max CPU frequency as default**: 33% faster API operations. No config changes needed. Timing-sensitive code (IR, bitbanging) may need review. Route to **Volt**.
- **40KB extra IRAM unlocked** for ESP32.
- **Signed OTA verification** (`ota: verify_signature: true`). Route to **Volt** plus **Vera**.
- **Custom partition tables** in `esp32:` block for configs that overflow default flash layout.
- **GPIO Expander interrupt_pin**: MCP23017, PCF8574, and others can now interrupt instead of polling. Route to **Volt**.
- **SPI Ethernet expansion**: W5500, W5100/W5100S, W6100/W6300, ENC28J60 (Microchip 10BASE-T). Wired networking for ESP32 and RP2040 devices without WiFi. Route to **Volt** plus **Grid**.
- **Client-side state logging**: up to 46x faster sensor publishing, auto-enabled.
- **ESP8266 crash handler** now matches ESP32/RP2040 quality.
- **Substitution system redesign**: up to 18x faster config loading. Dynamic `!include` paths.
- **2026.4.5 patch (bugfix only, no new components)**: ha-addon Device Builder toggle, secrets bundle fix when `!secret` quoted, substitutions sibling refs, WiFi safe mode, Nextion text sensor.

## ESPHome 2026.3
- **IR/RF Proxy** (`ir_rf_proxy`) — Runtime IR/RF signal transmission without reflashing. Learns and replays commands. Works with `remote_transmitter` / `remote_receiver`. → Route to **Volt**
- **RP2040 / RP2350 first-class support** — pico-sdk 2.0, 143+ board definitions, BLE foundations, crash diagnostics. → Route to **Volt**
- **Media player redesign** — Pluggable sources, playlists, Ogg Opus support. → Route to **Echo**
- **Performance** — Main loop up to 99x faster, API protobuf 6–12x faster, 11–20KB flash savings. No config changes needed — just reflash.
- **ESP8266 heap crash fix** — Long-standing LWIP use-after-free bug resolved.
