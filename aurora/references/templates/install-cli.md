# INSTALL.md template — Local ESPHome CLI

Template for `INSTALL.md` when the user picked **Local ESPHome CLI** as
the deployment method. Aurora/Volt fills in the placeholders.

Placeholders:

- `{device_name}` — the ESPHome `name:` value
- `{yaml_filename}` — the YAML filename
- `{board_model}` — specific board
- `{user_language}` — write all human text in the user's detected language

---

```markdown
# Installation — Local ESPHome CLI

This path gives you the most control. ESPHome runs on your computer,
compiles the firmware locally, and flashes the device over USB.

## Prerequisites

- Python 3.9 or newer (`python --version` to check)
- pip (`pip --version`)
- A USB-C cable for the first flash
- ~500 MB free disk space for the ESP32 toolchain (downloaded once)

## Steps

### 1. Install ESPHome

In a terminal in this project folder:

```
pip install esphome
```

Verify:

```
esphome version
```

Expected: a version string like `2026.4.5` or newer.

### 2. Set up secrets

Copy and edit the secrets file (do **not** commit `secrets.yaml`):

PowerShell (Windows):

```
Copy-Item secrets.yaml.example secrets.yaml
notepad secrets.yaml
```

bash (macOS / Linux):

```
cp secrets.yaml.example secrets.yaml
${EDITOR:-nano} secrets.yaml
```

Fill in:

- `wifi_ssid` and `wifi_password` for your WiFi
- `api_encryption_key`: generate one with
  `openssl rand -base64 32` (or
  `[Convert]::ToBase64String((1..32 | % { Get-Random -Maximum 256 }))` in PowerShell)
- `ota_password`: any strong password

### 3. Flash the device

Plug the `{board_model}` into a USB-C port. Then:

```
esphome run {yaml_filename}
```

ESPHome will:

1. Validate the YAML.
2. Compile the firmware (5-15 minutes the first time as toolchains
   download; ~30 seconds after that, cached).
3. Detect the serial port automatically and flash.
4. Stream logs from the device after boot.

Press `Ctrl-C` to stop streaming logs. The device keeps running.

### 4. Verify

While logs are streaming, look for:

- `WiFi connected, IP=<your-IP>` — networking works
- `API server listening on port 6053` — HA can connect
- No `ERROR` or `WARN` lines about your sensors

In Home Assistant: **Settings → Devices & services → Add Integration
→ ESPHome → {device_name}.local**. The entities Volt named appear
automatically.

## Future updates

Edit `{yaml_filename}`, then:

```
esphome run {yaml_filename}
```

After the first flash, ESPHome uses OTA over WiFi automatically — no
USB cable needed.

## If flashing fails

- **No serial port found**: the USB-UART driver is missing. Install
  CP210x (Silicon Labs) or CH340 depending on your board's chip.
- **Permission denied on /dev/ttyUSB0** (Linux):
  `sudo usermod -aG dialout $USER`, then log out and back in.
- **Brownout detector triggered**: insufficient USB power. Use a
  powered hub or a 1A+ wall adapter with a data-capable cable.
- **Compilation error**: ESPHome version may be too old. Run
  `pip install --upgrade esphome`.
```
