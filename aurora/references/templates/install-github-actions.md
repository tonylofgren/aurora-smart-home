# INSTALL.md template — GitHub Actions + web.esphome.io

Template for `INSTALL.md` when the user picked **GitHub Actions** as
the deployment method. Aurora/Volt fills in the placeholders.

Placeholders:

- `{device_name}` — the ESPHome `name:` value
- `{yaml_filename}` — the YAML filename
- `{board_model}` — specific board
- `{repo_name}` — the GitHub repo name (Aurora suggests one based on
  the project slug; user can rename)
- `{user_language}` — write all human text in the user's detected language

This template assumes Volt also placed `.github/workflows/build-firmware.yml`
and `manifest.json` in the project folder. See
`build-firmware-workflow.yml` for the workflow template.

---

```markdown
# Installation — GitHub Actions + web.esphome.io

Use this if you do not run Home Assistant and you do not want to
install Python locally. GitHub compiles the firmware for you and
publishes a `.bin` file. You then flash it from your browser.

## Prerequisites

- A GitHub account (free plan is enough)
- The `gh` CLI installed locally (optional but easier), or git + a web
  browser
- A USB-C cable for the first flash
- A Chrome/Edge browser with Web Serial support (Firefox does not
  support Web Serial as of 2026)

## Steps

### 1. Create the GitHub repo

With `gh` CLI:

```
cd <this project folder>
git init -b main
git add .
git commit -m "initial: {device_name}"
gh repo create {repo_name} --public --source=. --push
```

Without `gh` CLI: create an empty public repo at github.com/new called
`{repo_name}`, then:

```
cd <this project folder>
git init -b main
git add .
git commit -m "initial: {device_name}"
git remote add origin https://github.com/<your-username>/{repo_name}.git
git push -u origin main
```

### 2. Set up secrets

The workflow needs WiFi credentials, an API key, and an OTA password.
Add them as **GitHub Actions secrets** (not committed to git):

1. Open the repo on GitHub → **Settings** → **Secrets and variables**
   → **Actions** → **New repository secret**.
2. Add these secrets one by one (names must match `secrets.yaml.example`):
   - `WIFI_SSID`
   - `WIFI_PASSWORD`
   - `API_ENCRYPTION_KEY` (generate with
     `openssl rand -base64 32` or PowerShell
     `[Convert]::ToBase64String((1..32 | % { Get-Random -Maximum 256 }))`)
   - `OTA_PASSWORD` (any strong password)

### 3. Trigger the build

The workflow runs automatically on every push to `main`. To trigger
it manually:

- GitHub repo → **Actions** → **Build firmware** → **Run workflow**.

Wait 5-15 minutes for the first build (toolchains download once and
cache after that). Subsequent builds take 1-2 minutes.

### 4. Download and flash

When the workflow finishes, it creates a **GitHub Release** named
`firmware-<commit-sha>`. Open the release page and copy the URL to
`manifest.json` (right-click the asset → Copy link).

Open https://web.esphome.io/?url=&lt;manifest-url&gt; in Chrome or Edge:

1. Plug the `{board_model}` into a USB-C port.
2. Click **CONNECT** in the page.
3. Select the serial port (looks like `USB JTAG/serial debug unit` or
   `Silicon Labs CP210x`).
4. Click **INSTALL** → **Install {device_name}** → confirm.
5. Wait for the progress bar. The device reboots automatically.

### 5. Verify

After flashing, the device announces itself via mDNS as
`{device_name}.local`. Open `http://{device_name}.local` in your
browser to see the ESPHome web dashboard with live logs and OTA
update controls.

## Future updates

Edit `{yaml_filename}` locally, commit, push. The workflow rebuilds
and publishes a new release automatically. Either:

- Flash from web.esphome.io with the new manifest URL, or
- Use OTA via `http://{device_name}.local` → upload the new `.bin`.

## If the workflow fails

- Check the Actions tab logs. The most common failures are:
  - Missing secret → add it under Settings → Secrets.
  - Out-of-quota → GitHub free tier resets monthly.
  - Compilation error in YAML → fix locally, push again.
```
