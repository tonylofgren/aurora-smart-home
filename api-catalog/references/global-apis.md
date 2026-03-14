# Global APIs

Covers OpenAI, Spotify, Google Calendar, Telegram Bot API, and GitHub.

---

## OpenAI

**What it provides:** GPT-4o/GPT-4/GPT-3.5 text generation, DALL-E image generation, Whisper
speech-to-text, TTS, embeddings. Useful for voice command parsing, notification summarization,
and AI-driven automations.

**Auth:** API key in header (`Authorization: Bearer {key}`)
**Base URL:** `https://api.openai.com/v1`
**Get key:** platform.openai.com → API keys → Create new secret key
**Rate limit:** Depends on tier. Free: RPM limited. Paid: generous limits by model
**Cost:** Pay per token. GPT-4o-mini: ~$0.15/1M tokens input

### Key endpoints

**Chat completion (GPT-4o-mini):**
```
POST https://api.openai.com/v1/chat/completions
Headers: Authorization: Bearer {key}, Content-Type: application/json
Body:
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "You are a home automation assistant."},
    {"role": "user", "content": "Parse this voice command: turn on the kitchen lights"}
  ],
  "max_tokens": 100
}
```

**Speech-to-text (Whisper):**
```
POST https://api.openai.com/v1/audio/transcriptions
Headers: Authorization: Bearer {key}
Body (multipart): file={audio.wav}, model=whisper-1
```

**DALL-E image generation:**
```
POST https://api.openai.com/v1/images/generations
Body: {"model": "dall-e-3", "prompt": "cozy smart home interior", "size": "1024x1024"}
```

### Node-RED implementation — voice command parser

```javascript
// Function node — build OpenAI request for command parsing
const command = msg.payload; // e.g., "make the living room dim and warm"

msg.payload = JSON.stringify({
    model: "gpt-4o-mini",
    messages: [
        {
            role: "system",
            content: `You parse smart home voice commands into JSON.
Return: {"action": "turn_on|turn_off|set_brightness|set_temperature",
         "entity": "entity_id",
         "value": number_or_null}
Only return JSON, no explanation.`
        },
        { role: "user", content: command }
    ],
    max_tokens: 100
});
msg.headers = {
    "Authorization": "Bearer " + env.get("OPENAI_KEY"),
    "Content-Type": "application/json"
};
return msg;
```

```javascript
// Function node — parse response and call HA service
const response = JSON.parse(msg.payload.choices[0].message.content);

msg.payload = {
    action: `${response.action.replace("_", ".")}`,
    target: { entity_id: response.entity },
    data: response.value ? { brightness_pct: response.value } : {}
};
return msg;
```

### HA YAML notify

```yaml
# Summarize a sensor history via OpenAI — call from automation
rest_command:
  openai_chat:
    url: https://api.openai.com/v1/chat/completions
    method: POST
    headers:
      Authorization: !secret openai_bearer
      Content-Type: application/json
    payload: >
      {"model": "gpt-4o-mini",
       "messages": [{"role": "user", "content": "{{ prompt }}"}],
       "max_tokens": 200}
```

```yaml
# secrets.yaml
openai_bearer: "Bearer sk-..."
```

---

## Spotify

**What it provides:** Playback control (play/pause/skip/volume), current track info, playlist
management, search. Great for music automations (play music when you arrive home, stop when
you leave, etc.).

**Auth:** OAuth2 — authorization code flow. Access token expires after 1 hour, refresh token
is long-lived.
**Base URL:** `https://api.spotify.com/v1`
**Get credentials:** developer.spotify.com → Create App → Client ID + Secret
**Free tier:** Full API access, requires Spotify Premium for playback control
**Rate limit:** ~100 req/s (generous for home use)

### Step 1: OAuth2 setup

The OAuth2 flow requires a redirect URL. For home automation, use a local script or the
[Spotipy](https://github.com/spotipy-dev/spotipy) Python library to get the initial tokens,
then store the refresh token.

**Quick token via PKCE (browser):**
1. Open: `https://accounts.spotify.com/authorize?response_type=code&client_id={ID}&scope=user-read-playback-state+user-modify-playback-state&redirect_uri=http://localhost:8888/callback`
2. Log in → copy code from URL
3. Exchange for tokens: `POST https://accounts.spotify.com/api/token`

### Step 2: Refresh access token (every ~50 min)

```
POST https://accounts.spotify.com/api/token
Headers: Authorization: Basic {BASE64(client_id:client_secret)}
Body (form): grant_type=refresh_token&refresh_token={REFRESH_TOKEN}

Response: {"access_token": "...", "expires_in": 3600}
```

### Key endpoints

```
GET  /v1/me/player                    → current playback state
GET  /v1/me/player/currently-playing  → current track
PUT  /v1/me/player/play               → play/resume
PUT  /v1/me/player/pause              → pause
POST /v1/me/player/next               → skip to next
PUT  /v1/me/player/volume             → set volume (0-100)
GET  /v1/search?q={query}&type=playlist → search
```

### Node-RED implementation

```
[inject: on arrival home]
  → [function: build play request]
  → [http request: PUT /me/player/play]
  → [debug: confirm]
```

```javascript
// Function node — play a specific playlist on device
msg.method = "PUT";
msg.url = "https://api.spotify.com/v1/me/player/play";
msg.headers = {
    "Authorization": "Bearer " + flow.get("spotifyToken"),
    "Content-Type": "application/json"
};
msg.payload = JSON.stringify({
    context_uri: "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M", // Your playlist URI
    device_id: env.get("SPOTIFY_DEVICE_ID") // Optional: target device
});
return msg;
```

```javascript
// Function node — extract current track for display
const item = msg.payload.item;
if (!item) { msg.payload = null; return msg; }

msg.payload = {
    action: "input_text.set_value",
    target: { entity_id: "input_text.now_playing" },
    data: {
        value: `${item.name} — ${item.artists.map(a => a.name).join(", ")}`
    }
};
return msg;
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 15
    resource: https://api.spotify.com/v1/me/player/currently-playing
    headers:
      Authorization: !secret spotify_token
    sensor:
      - name: "Spotify Track"
        value_template: >-
          {% if value_json and value_json.item %}
            {{ value_json.item.name }}
          {% else %}
            Nothing playing
          {% endif %}
      - name: "Spotify Artist"
        value_template: >-
          {% if value_json and value_json.item %}
            {{ value_json.item.artists[0].name }}
          {% else %}
            —
          {% endif %}
      - name: "Spotify Is Playing"
        value_template: "{{ value_json.is_playing | default(false) }}"
```

> **Tip:** The [Spotify integration](https://www.home-assistant.io/integrations/spotify/) is
> built into Home Assistant and handles OAuth2 token refresh automatically. Use it unless you
> need data the integration doesn't expose.

---

## Google Calendar

**What it provides:** Read/write Google Calendar events. Useful for presence-based automations,
"do not disturb" mode when in a meeting, scheduling heating/cooling around your calendar.

**Auth:** OAuth2 — service account (server-to-server) or user OAuth2.
For home automation, service account is simplest.
**Base URL:** `https://www.googleapis.com/calendar/v3`
**Get credentials:** console.cloud.google.com → Calendar API → Service Account + JSON key
**Rate limit:** 1,000,000 req/day (free)

### Step 1: Service account setup

1. console.cloud.google.com → New project → Enable Google Calendar API
2. IAM → Service Accounts → Create → Download JSON key
3. Share your calendar with the service account email (give it Reader access)

### Step 2: Get access token (JWT-based)

```python
# Python helper to get service account token (run once to get token)
from google.oauth2 import service_account
import google.auth.transport.requests

creds = service_account.Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/calendar.readonly"]
)
creds.refresh(google.auth.transport.requests.Request())
print(creds.token)  # Use this in Node-RED, valid ~1 hour
```

### Key endpoints

```
GET /calendars/{calendarId}/events
  ?timeMin=2026-03-14T00:00:00Z
  &timeMax=2026-03-14T23:59:59Z
  &singleEvents=true
  &orderBy=startTime
```

### Node-RED implementation

```javascript
// Function node — check if currently in a meeting
const events = msg.payload.items || [];
const now = new Date();

const inMeeting = events.some(event => {
    const start = new Date(event.start.dateTime || event.start.date);
    const end = new Date(event.end.dateTime || event.end.date);
    return start <= now && end >= now;
});

msg.payload = {
    action: "input_boolean.turn_" + (inMeeting ? "on" : "off"),
    target: { entity_id: "input_boolean.in_meeting" },
    data: {}
};
return msg;
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 300
    resource: "https://www.googleapis.com/calendar/v3/calendars/primary/events?maxResults=5&singleEvents=true&orderBy=startTime&timeMin={{ utcnow().strftime('%Y-%m-%dT%H:%M:%SZ') }}"
    headers:
      Authorization: !secret google_calendar_token
    sensor:
      - name: "Next Calendar Event"
        value_template: >-
          {% set events = value_json.items %}
          {% if events %}{{ events[0].summary }}{% else %}Free{% endif %}
      - name: "Next Event Start"
        value_template: >-
          {% set events = value_json.items %}
          {% if events %}{{ events[0].start.dateTime | default(events[0].start.date) }}{% else %}—{% endif %}
```

> **Tip:** The [Google Calendar integration](https://www.home-assistant.io/integrations/google/)
> handles OAuth2 and provides calendar events as HA calendar entities. Much simpler than DIY.

---

## Telegram Bot API

**What it provides:** Send and receive messages via Telegram. Excellent for HA notifications,
interactive commands ("Are you sure you want to unlock the front door? [Yes] [No]"),
and security alerts with camera snapshots.

**Auth:** Bot token in URL — no OAuth2 needed
**Base URL:** `https://api.telegram.org/bot{TOKEN}`
**Get token:** Telegram → @BotFather → /newbot → copy token
**Rate limit:** 30 messages/s to different users, 20 messages/min to same chat

### Setup

1. Message @BotFather: `/newbot` → name your bot → copy token
2. Start a chat with your bot (search by username)
3. Get your chat ID: `GET https://api.telegram.org/bot{TOKEN}/getUpdates` → find `chat.id`

### Key endpoints

```
POST /sendMessage
  Body: {"chat_id": 123456, "text": "Motion detected!", "parse_mode": "HTML"}

POST /sendPhoto
  Body: {"chat_id": 123456, "photo": "https://url-to-image.jpg", "caption": "Front door"}

POST /sendDocument
  Body: {"chat_id": 123456, "document": file_url}

GET /getUpdates
  Body: {"offset": last_update_id}  → poll for incoming messages

POST /answerCallbackQuery           → respond to inline button presses
POST /sendMessage with reply_markup → send messages with inline buttons
```

### Node-RED implementation — alert with buttons

```javascript
// Function node — send alert with Yes/No buttons
msg.method = "POST";
msg.url = `https://api.telegram.org/bot${env.get("TELEGRAM_TOKEN")}/sendMessage`;
msg.payload = JSON.stringify({
    chat_id: env.get("TELEGRAM_CHAT_ID"),
    text: "⚠️ <b>Motion detected</b> at front door.\nUnlock the door?",
    parse_mode: "HTML",
    reply_markup: JSON.stringify({
        inline_keyboard: [[
            { text: "🔓 Yes, unlock", callback_data: "unlock_door" },
            { text: "❌ No", callback_data: "ignore" }
        ]]
    })
});
msg.headers = { "Content-Type": "application/json" };
return msg;
```

```javascript
// Function node — poll for button presses (runs every 2s)
const updates = msg.payload.result;
if (!updates || updates.length === 0) return null;

const latest = updates[updates.length - 1];
if (!latest.callback_query) return null;

const action = latest.callback_query.data;
if (action === "unlock_door") {
    msg.payload = {
        action: "lock.unlock",
        target: { entity_id: "lock.front_door" },
        data: {}
    };
    return msg;
}
return null;
```

### HA YAML — Telegram notify + bot

```yaml
# configuration.yaml
telegram_bot:
  - platform: polling
    api_key: !secret telegram_bot_token
    allowed_chat_ids:
      - !secret telegram_chat_id

notify:
  - platform: telegram
    name: "telegram"
    chat_id: !secret telegram_chat_id
```

```yaml
# secrets.yaml
telegram_bot_token: "1234567890:ABC..."
telegram_chat_id: 123456789
```

```yaml
# Example automation — motion alert
automation:
  - alias: "Motion alert with photo"
    trigger:
      - trigger: state
        entity_id: binary_sensor.front_door_motion
        to: "on"
    action:
      - action: notify.telegram
        data:
          title: "Motion detected"
          message: "Front door motion at {{ now().strftime('%H:%M') }}"
```

> **Tip:** The [Telegram Bot integration](https://www.home-assistant.io/integrations/telegram/)
> is built into Home Assistant. Use `notify.telegram` for simple notifications. The Node-RED
> approach is better for interactive workflows with button callbacks.

---

## GitHub

**What it provides:** Repository info, issue tracking, workflow dispatch (trigger CI/CD),
release monitoring. Useful for OTA firmware automation (trigger build when you push), and
monitoring home automation project updates.

**Auth:** Personal Access Token (PAT) in header — classic or fine-grained
**Base URL:** `https://api.github.com`
**Get token:** github.com → Settings → Developer Settings → Personal Access Tokens → Fine-grained
**Rate limit:** 5,000 req/hour (authenticated), 60 req/hour (unauthenticated)

### Key endpoints

```
GET  /repos/{owner}/{repo}/releases/latest → latest release info
GET  /repos/{owner}/{repo}/releases        → all releases
POST /repos/{owner}/{repo}/dispatches      → trigger workflow
GET  /repos/{owner}/{repo}/actions/workflows/{id}/runs → workflow run status
GET  /repos/{owner}/{repo}/issues          → issues list
POST /repos/{owner}/{repo}/issues          → create issue
```

### Node-RED — check for firmware updates

```javascript
// Function node — check latest release vs installed version
const latest = msg.payload.tag_name; // e.g., "v1.3.2"
const installed = flow.get("firmwareVersion") || "v1.0.0";

if (latest !== installed) {
    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "Firmware update available",
            message: `New version: ${latest} (installed: ${installed})`
        }
    };
    return msg;
}
return null;
```

### Node-RED — trigger CI build on code push

```javascript
// Function node — dispatch GitHub Actions workflow
msg.method = "POST";
msg.url = "https://api.github.com/repos/myuser/myrepo/dispatches";
msg.headers = {
    "Authorization": "Bearer " + env.get("GITHUB_TOKEN"),
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
};
msg.payload = JSON.stringify({
    event_type: "build-firmware",
    client_payload: {
        version: "1.4.0",
        target: "esp32"
    }
});
return msg;
```

### HA YAML REST sensor — latest release monitor

```yaml
rest:
  - scan_interval: 3600
    resource: "https://api.github.com/repos/home-assistant/core/releases/latest"
    headers:
      Authorization: !secret github_token
      Accept: application/vnd.github+json
    sensor:
      - name: "HA Latest Release"
        value_template: "{{ value_json.tag_name }}"
      - name: "HA Release Date"
        value_template: "{{ value_json.published_at }}"
      - name: "HA Release Notes URL"
        value_template: "{{ value_json.html_url }}"
```

```yaml
# secrets.yaml
github_token: "Bearer github_pat_..."
```

### Automation — notify on new HA release

```yaml
automation:
  - alias: "HA new release notification"
    trigger:
      - trigger: state
        entity_id: sensor.ha_latest_release
    condition:
      - condition: template
        value_template: >
          {{ states('sensor.ha_latest_release') !=
             state_attr('update.home_assistant_core_update', 'installed_version') }}
    action:
      - action: notify.telegram
        data:
          message: "Home Assistant {{ states('sensor.ha_latest_release') }} is available!"
```
