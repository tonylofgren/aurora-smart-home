# INSTALL.md template — HA ESPHome Add-on

> ⚠️ **TRANSLATE-FIRST.** This template is English. Translate every heading, prose paragraph, prerequisite, step description, and verification text into the user's detected language before writing the result to `<project>/esphome/INSTALL.md`. Quoted commands, file paths, `!secret` keys, and identifiers stay English. Shipping this verbatim to a non-English user is a Language Rule violation per `aurora/SKILL.md`.

Template for `INSTALL.md` when the user picked **HA ESPHome Add-on** as
the deployment method. Aurora/Volt fills in the placeholders.

Placeholders:

- `{device_name}` — the ESPHome `name:` value (e.g. `co2_monitor_living_room`)
- `{yaml_filename}` — the YAML filename (e.g. `co2-monitor.yaml`)
- `{board_model}` — specific board (e.g. `ESP32-S3-DevKitC-1`)
- `{user_language}` — write all human text in the user's detected language

---

```markdown
# Installation — Home Assistant ESPHome Add-on

This is the simplest path. Home Assistant compiles the firmware
server-side and flashes via USB or OTA. No local tools needed.

## Prerequisites

- Home Assistant Core or HA OS running (any 2024.x or later)
- The **ESPHome Builder** add-on installed (Settings → Add-ons →
  ESPHome Builder → Install). On HA Core, install ESPHome separately
  via Docker or pip.
- USB-C cable for the initial flash. After that, OTA works wirelessly.

## Steps

1. **Open ESPHome Builder** in Home Assistant.
2. Click **+ New device** (top right). Pick **Continue** when asked
   about the device name — the YAML already has it set.
3. When prompted to install, choose **Skip and let me edit the file**.
4. Find your new device in the list. Click the three dots → **Edit**.
5. Replace the placeholder YAML with the contents of `{yaml_filename}`
   from this project folder. Save.
6. Click the three dots again → **Validate**. Fix any reported issues
   (usually credentials in `secrets.yaml` — see below).
7. Set up `secrets.yaml`:
   - In the same view, click the **Secrets** button at the top right.
   - Copy the contents of `secrets.yaml.example` from this project.
   - Replace placeholders with real values (WiFi SSID, password, API key,
     OTA password). Save.
8. Click **Install**. Choose **Plug into the computer running Home
   Assistant** for the first flash (or **Manual download** if HA runs
   on a remote server — flash the resulting `.bin` from a machine with
   USB access).
9. Wait 5-15 minutes for the first compile. Toolchains cache after
   that, so subsequent builds take 30 seconds.
10. After the device boots and joins WiFi, it auto-appears in
    Home Assistant under **Settings → Devices & services → ESPHome**.
    Click **Configure** to add the entities to a dashboard.

## Verifying it works

- The ESPHome dashboard shows the device as **ONLINE** (green dot).
- The device's logs (three dots → **Logs**) show no `ERROR` lines and
  a `WiFi connected` line.
- The entities Volt named (e.g. `sensor.{device_name}_co2`) appear in
  Developer Tools → States.

## If it does not boot

- Check the wiring against `WIRING.md` (or the Wiring section in
  `README.md`). Wrong polarity on a 3.3V/GND swap will brick the
  device until you reflash via USB.
- Check the logs in the ESPHome dashboard for `ESP32 boot loop` or
  `Brownout detector triggered` — the latter means insufficient power
  on USB; try a powered hub or a wall adapter rated 1A or more.
- USB enumeration on `{board_model}` requires the **CP210x** or
  **CH340** driver depending on the USB-UART chip. If the board does
  not appear as a serial port, install the matching driver.
```
