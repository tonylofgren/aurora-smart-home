# Smart Home Cloud APIs

Covers Shelly Cloud, Tuya IoT Platform, Philips Hue (local Bridge), and IKEA Dirigera.

---

## Shelly Cloud

**What it provides:** Remote control and status of Shelly devices (switches, dimmers, plugs, sensors)
via Shelly's cloud service. Works even outside local network.

**Auth:** API key (Cloud Key from Shelly app)
**Base URL:** `https://shelly-{region}-1.shelly.cloud` (e.g., `shelly-eu-1.shelly.cloud`)
**Get key:** Shelly app → My Account → Security → Cloud Key
**Rate limit:** ~1 req/s recommended

> **Prefer local?** Shelly devices expose a full local REST API on their IP without any cloud
> dependency. Use the local API for automations that require low latency or offline reliability.

### Local REST API (recommended for automations)

No auth needed by default (optional digest auth can be enabled):

```
GET http://{device-ip}/relay/0         → read relay state
GET http://{device-ip}/relay/0?turn=on → turn on
GET http://{device-ip}/relay/0?turn=off → turn off
GET http://{device-ip}/status          → full device status
```

**Gen2+ devices (Plus/Pro series) use RPC:**
```
POST http://{device-ip}/rpc/Switch.Set
Body: {"id": 0, "on": true}

GET http://{device-ip}/rpc/Switch.GetStatus
Body: {"id": 0}
```

### Cloud API

```
POST https://shelly-eu-1.shelly.cloud/device/relay/control
Headers: Content-Type: application/x-www-form-urlencoded
Body: auth_key={CLOUD_KEY}&id={device-id}&channel=0&turn=on
```

**Get device ID:** Shelly app → Device → Settings → Device info → Device ID

### Node-RED local implementation

```
[inject: trigger]
  → [http request: GET http://192.168.1.100/relay/0?turn=on]
  → [debug: confirm]
```

**Function node — read Shelly status:**
```javascript
// Parse Shelly Gen1 status response
const status = msg.payload;
const isOn = status.relays[0].ison;
const power = status.meters ? status.meters[0].power : null;

msg.payload = {
    action: "homeassistant.update_entity",
    target: { entity_id: "switch.shelly_living_room" },
    data: { state: isOn ? "on" : "off" }
};
return msg;
```

### HA YAML REST sensor (local)

```yaml
# Gen1 Shelly
rest:
  - scan_interval: 10
    resource: "http://192.168.1.100/status"
    sensor:
      - name: "Shelly Relay State"
        value_template: "{{ 'on' if value_json.relays[0].ison else 'off' }}"
      - name: "Shelly Power"
        value_template: "{{ value_json.meters[0].power }}"
        unit_of_measurement: "W"
        device_class: power

rest_command:
  shelly_on:
    url: "http://192.168.1.100/relay/0?turn=on"
  shelly_off:
    url: "http://192.168.1.100/relay/0?turn=off"
```

> **Tip:** The official [Shelly integration](https://www.home-assistant.io/integrations/shelly/) in
> Home Assistant handles Shelly devices natively over local network via CoAP/MQTT — no REST needed.
> Use the REST approach only for devices the integration doesn't support.

---

## Tuya IoT Platform

**What it provides:** Cloud control of Tuya/Smart Life devices — a huge range of Chinese smart home
products sold under hundreds of brands. Also exposes device state, scenes, and IR blasters.

**Auth:** OAuth2 (client credentials flow) — access token rotates every 2 hours
**Base URL:** `https://openapi.tuyaeu.com` (EU), `https://openapi.tuyaus.com` (US)
**Get credentials:** iot.tuya.com → Cloud → Create project → Get Access ID + Secret
**Rate limit:** Varies by plan. Free tier: 10,000 API calls/month

> **Important:** Tuya requires pairing devices with the Tuya IoT Platform. Add your Smart Life account
> to the cloud project so your devices are linked.

### Step 1: Get access token

```
POST https://openapi.tuyaeu.com/v1.0/token?grant_type=1
Headers:
  client_id: {ACCESS_ID}
  sign: {HMAC-SHA256 signature — see below}
  t: {unix timestamp ms}
  sign_method: HMAC-SHA256
```

The signature is: `HMAC-SHA256(ACCESS_ID + t + "" + ACCESS_SECRET)` — Tuya's auth is complex.
Use the [tinytuya](https://github.com/jasonacox/tinytuya) Python library or the HA integration instead.

### Node-RED implementation (simplified via tinytuya service)

The easiest approach is running a local `tinytuya` REST server in Docker:

```
[inject: every 30s]
  → [http request: GET http://localhost:8888/devices/{device-id}]
  → [function: extract state + DPS values]
  → [api-call-service: update HA entity]
```

```yaml
# docker-compose.yml for tinytuya REST server
services:
  tinytuya:
    image: jasonacox/tinytuya:latest
    ports:
      - "8888:8888"
    volumes:
      - ./tinytuya:/app/config
```

### HA YAML (via LocalTuya or Tuya integration)

The [LocalTuya](https://github.com/rospogrigio/localtuya) HACS integration is strongly recommended
for local control without cloud dependency:

```yaml
# After installing LocalTuya via HACS, configure in UI
# LocalTuya discovers devices on your local network
# Requires: device local key (get via tinytuya wizard)
```

```
Use the ha-integration skill with this prompt:
"Create a Tuya IoT Platform integration that handles OAuth2 token refresh automatically.
Entities: switch control (on/off), power monitoring (W, kWh).
Use v1.0/token for auth and v1.0/iot-03/devices/{id}/commands for control.
Poll status every 30 seconds."
```

---

## Philips Hue (Local Bridge API)

**What it provides:** Full control of Hue lights, groups, scenes, sensors, and schedules via
local Bridge — no cloud required, very low latency.

**Auth:** One-time button-press to create a username token
**Base URL:** `https://{bridge-ip}/api`  (also `https://{bridge-ip}/clip/v2` for v2 API)
**Rate limit:** ~10 req/s on the bridge (burst ok, sustained low)
**Requirement:** Philips Hue Bridge (v2 recommended)

### Step 1: Find bridge IP

```
GET https://discovery.meethue.com/
Response: [{"id": "...", "internalipaddress": "192.168.1.50"}]
```

### Step 2: Create username (one-time setup)

Press the link button on the bridge, then within 30 seconds:

```
POST http://{bridge-ip}/api
Body: {"devicetype": "my_home_assistant#node_red"}

Response: [{"success": {"username": "abc123..."}}]
```

Save this username as your API key.

### Key endpoints (v1 API)

```
GET /api/{username}/lights             → all lights + state
GET /api/{username}/lights/{id}        → specific light
PUT /api/{username}/lights/{id}/state  → control light
GET /api/{username}/groups             → rooms/zones
PUT /api/{username}/groups/{id}/action → control group/scene
GET /api/{username}/sensors            → motion/temperature sensors
```

**Turn on a light with color:**
```
PUT http://{bridge-ip}/api/{username}/lights/1/state
Body: {"on": true, "bri": 200, "hue": 8000, "sat": 200}
```

**Activate a scene:**
```
PUT http://{bridge-ip}/api/{username}/groups/1/action
Body: {"scene": "abc123"}
```

### Node-RED implementation

```
[inject: trigger or HA event]
  → [function: build Hue command]
  → [http request: PUT to bridge]
  → [debug: confirm response]
```

**Function node — adaptive brightness based on time:**
```javascript
const hour = new Date().getHours();
let bri, ct;

if (hour >= 6 && hour < 12) {
    bri = 254; ct = 6500; // Bright, cool morning
} else if (hour >= 12 && hour < 18) {
    bri = 200; ct = 4000; // Neutral afternoon
} else {
    bri = 100; ct = 2700; // Warm, dim evening
}

msg.method = "PUT";
msg.url = `http://192.168.1.50/api/YOUR_USERNAME/lights/1/state`;
msg.payload = { on: true, bri, ct };
return msg;
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 30
    resource: "http://192.168.1.50/api/YOUR_USERNAME/lights/1"
    sensor:
      - name: "Hue Light State"
        value_template: "{{ 'on' if value_json.state.on else 'off' }}"
      - name: "Hue Brightness"
        value_template: "{{ value_json.state.bri }}"
      - name: "Hue Color Temp"
        value_template: "{{ value_json.state.ct }}"

rest_command:
  hue_scene:
    url: "http://192.168.1.50/api/YOUR_USERNAME/groups/1/action"
    method: PUT
    headers:
      Content-Type: application/json
    payload: '{"scene": "{{ scene_id }}"}'
```

> **Tip:** The [Philips Hue integration](https://www.home-assistant.io/integrations/hue/) is built
> into Home Assistant and handles all of this automatically. Use the REST/Node-RED approach only for
> custom automations not possible through the official integration.

### Full HACS integration

```
Use the ha-integration skill with this prompt:
"Create a Philips Hue v2 (CLIP API) integration using the local bridge.
Auth: one-time username via button press, store in config entry.
Entities: light (on/off, brightness, color temp, RGB, xy), group (on/off, scene activation),
motion sensor (motion, lux, temperature).
Use SSE event stream /eventstream/clip/v2 for push updates.
HACS-ready."
```

---

## IKEA Dirigera (local API)

**What it provides:** Control IKEA TRÅDFRI/Dirigera smart home products — bulbs, sockets, blinds,
air purifiers, sensors — via the local Dirigera hub. No cloud required.

**Auth:** OAuth-like: PKCE challenge + button press on hub → access token (long-lived)
**Base URL:** `https://{dirigera-ip}:8443/v1`
**Self-signed cert:** Hub uses self-signed TLS — skip cert verification in requests
**Requirement:** IKEA Dirigera hub (not the old TRÅDFRI gateway)

### Step 1: Discover hub IP

```bash
# mDNS: hub advertises as _dirigera._tcp.local
# Or check DHCP leases / router admin panel
```

### Step 2: Get access token (one-time)

Generate a code verifier and challenge (PKCE), then:

```
POST https://{dirigera-ip}:8443/v1/oauth/authorize
Body (form): audience=homesmart.local&response_type=code
             &code_challenge={BASE64URL(SHA256(verifier))}
             &code_challenge_method=S256
```

Press the action button on the hub within 30 seconds, then exchange code:

```
POST https://{dirigera-ip}:8443/v1/oauth/token
Body (form): code={code}&name=my-automation&grant_type=authorization_code
             &code_verifier={verifier}

Response: {"access_token": "eyJ...", "token_type": "Bearer"}
```

This token is long-lived (years). Store it in secrets.

### Key endpoints

```
GET  /v1/devices                → all devices + state
GET  /v1/devices/{id}           → specific device
PATCH /v1/devices/{id}          → control device
GET  /v1/rooms                  → all rooms
GET  /v1/scenes                 → all scenes
POST /v1/scenes/{id}/trigger    → trigger a scene
```

**Turn on a light:**
```
PATCH https://{hub-ip}:8443/v1/devices/{device-id}
Headers: Authorization: Bearer {token}
Body: [{"attributes": {"isOn": true, "lightLevel": 80}}]
```

### Node-RED implementation

```javascript
// Function node — build IKEA Dirigera request
msg.method = "PATCH";
msg.url = `https://192.168.1.60:8443/v1/devices/${env.get("IKEA_DEVICE_ID")}`;
msg.headers = {
    "Authorization": "Bearer " + env.get("IKEA_TOKEN"),
    "Content-Type": "application/json"
};
msg.payload = [{ "attributes": { "isOn": true, "lightLevel": 70 } }];
msg.rejectUnauthorized = false; // self-signed cert
return msg;
```

```json
{
  "type": "http request",
  "method": "msg",
  "url": "msg",
  "tls": {"verifyServerCert": false},
  "ret": "obj"
}
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 30
    resource: "https://192.168.1.60:8443/v1/devices"
    headers:
      Authorization: !secret ikea_dirigera_token
    verify_ssl: false
    sensor:
      - name: "IKEA Device Count"
        value_template: "{{ value_json | length }}"
```

> **Tip:** The [IKEA integration](https://www.home-assistant.io/integrations/ikea_tradfri/) in
> Home Assistant supports Dirigera natively. The [python-dirigera](https://github.com/Leggin/dirigera)
> library also provides a clean Python wrapper for custom integrations.

### Full HACS integration

```
Use the ha-integration skill with this prompt:
"Create an IKEA Dirigera local integration.
Auth: long-lived Bearer token stored in config entry, PKCE flow for setup.
TLS: accept self-signed cert (verify=False in aiohttp).
Entities: light (on/off, brightness 0-100, color temp, RGB), outlet (on/off, power monitoring),
blind (position 0-100, tilt), air purifier (on/off, fan speed, auto mode, filter status),
motion sensor, temperature sensor, humidity sensor.
Poll every 30s. Use /v1/devices endpoint.
HACS-ready."
```
