# INSTALL.md template — Docker self-hosted ESPHome

Template for `INSTALL.md` when the user picked **Docker self-hosted
ESPHome** as the deployment method. Aurora/Volt fills in the
placeholders.

Placeholders:

- `{device_name}` — the ESPHome `name:` value
- `{yaml_filename}` — the YAML filename
- `{board_model}` — specific board
- `{user_language}` — write all human text in the user's detected language

This template assumes Volt also placed `docker-compose.yml` in the
project folder.

---

```markdown
# Installation — Docker self-hosted ESPHome dashboard

Use this if you want to run the ESPHome dashboard locally without
installing Python and without running Home Assistant. The Docker
container has everything (Python, ESPHome, PlatformIO, toolchains)
pre-installed.

Best for power users with a home server, NAS, or always-on Raspberry Pi.

## Prerequisites

- Docker Engine 24+ and Docker Compose v2 installed
  (`docker --version`, `docker compose version`)
- ~2 GB free disk space (~500 MB image + ~1.5 GB toolchain cache
  after first build)
- A USB-C cable for the first flash, with the host running Docker
  physically connected to the device — or a remote board reachable via
  network for OTA

## Steps

### 1. Start the ESPHome dashboard

In this project folder:

```
docker compose up -d
```

The dashboard becomes available at **http://localhost:6052** (or the
host's IP if running on a server). The compose file passes through:

- This project folder as the dashboard's config dir, so
  `{yaml_filename}` and `secrets.yaml` are already visible.
- `/dev/ttyUSB0` (Linux) or USB device on Windows/macOS — adjust the
  `devices:` section in `docker-compose.yml` if your serial port has
  a different path.

### 2. Set up secrets

Open the dashboard at http://localhost:6052. Click **Secrets** at the
top right. Paste the contents of `secrets.yaml.example` and fill in:

- `wifi_ssid`, `wifi_password`
- `api_encryption_key` (generate with
  `openssl rand -base64 32`)
- `ota_password` (any strong password)

Save.

### 3. Flash the device

In the dashboard, find `{device_name}`. Click **Install** →
**Plug into the computer running ESPHome Dashboard**. The first
compile takes 5-15 minutes (toolchains cache after that). Subsequent
flashes take 30 seconds.

After the device boots and joins WiFi, it auto-appears as **online**
in the dashboard.

### 4. Verify

The dashboard shows `{device_name}` as **ONLINE** (green dot). Click
**Logs** to see live output from the device. Look for `WiFi connected`
and no `ERROR` lines.

If you also run Home Assistant on the same network: HA discovers the
device automatically via the API encryption key. Add the integration
under **Settings → Devices & services → ESPHome**.

## Future updates

Edit `{yaml_filename}` in this folder (any editor; the dashboard sees
it live). Click **Install** in the dashboard. ESPHome uses OTA over
WiFi after the first flash — no USB cable needed.

## Stopping and starting

```
docker compose down       # stops the dashboard
docker compose up -d      # starts it again
docker compose logs -f    # tails the dashboard log
```

## If flashing fails

- **No USB device visible in container**: the host's USB device is not
  passed through. Edit `docker-compose.yml`'s `devices:` section to
  match your serial port (`/dev/ttyUSB0` on Linux, see Docker Desktop
  USB passthrough docs for Windows / macOS).
- **Compile fails on first run**: free disk space — toolchains need
  ~1.5 GB; clean unused Docker images with `docker system prune`.
- **Dashboard not reachable at localhost:6052**: another service is
  using that port. Change the `ports:` mapping in `docker-compose.yml`
  to `"6053:6052"` or another free port.
```

---

# docker-compose.yml template (Volt places this in the project folder)

```yaml
services:
  esphome:
    container_name: esphome-{device_name}
    image: ghcr.io/esphome/esphome:stable
    restart: unless-stopped
    ports:
      - "6052:6052"
    volumes:
      - .:/config
      - /etc/localtime:/etc/localtime:ro
    privileged: true
    devices:
      - /dev/ttyUSB0:/dev/ttyUSB0
    environment:
      ESPHOME_DASHBOARD_USE_PING: "true"
```
