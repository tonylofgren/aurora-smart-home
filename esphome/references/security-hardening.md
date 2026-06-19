# ESPHome Security Hardening Guide

Checklist and best practices for securing ESPHome devices.

## Security Checklist

### Essential (Must Have)

- [ ] **API encryption enabled** - Prevents eavesdropping on HA communication
- [ ] **OTA password set** - Prevents unauthorized firmware updates
- [ ] **secrets.yaml used** - No hardcoded credentials in config files
- [ ] **secrets.yaml in .gitignore** - Never commit credentials
- [ ] **Unique passwords per device** - Limits breach impact

### Recommended

- [ ] **Web server disabled** - Reduces attack surface
- [ ] **Fallback AP with password** - Secure recovery mode
- [ ] **Static IP configured** - Easier firewall rules
- [ ] **Network segmentation** - IoT VLAN isolation
- [ ] **Firewall rules** - Block internet access for devices

### Advanced

- [ ] **MQTT with TLS** - Encrypted broker communication
- [ ] **Disable unused components** - Minimize attack surface
- [ ] **Regular firmware updates** - Security patches
- [ ] **Physical security** - Tamper-resistant enclosures

---

## Implementation Details

### API Encryption

```yaml
api:
  encryption:
    key: !secret api_encryption_key

# Generate key with:
# python scripts/generate_secrets.py --output
# or
# openssl rand -base64 32
```

**Why:** Without encryption, API traffic is plaintext. Anyone on your network can intercept commands and sensor data.

### OTA Password

```yaml
ota:
  - platform: esphome
    password: !secret ota_password
```

**Why:** Without password, anyone on the network can flash malicious firmware to your device.

### Secrets Management

**secrets.yaml** (never commit this file):
```yaml
wifi_ssid: "YourNetwork"
wifi_password: "SecurePassword123"
api_encryption_key: "base64EncodedKey=="
ota_password: "AnotherSecurePassword"
fallback_ap_password: "FallbackPassword"
```

**config.yaml:**
```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  - platform: esphome
    password: !secret ota_password
```

**.gitignore:**
```
secrets.yaml
.esphome/
```

### Disable Web Server

```yaml
# Remove or comment out in production:
# web_server:
#   port: 80
```

**Why:** Web server exposes device status and controls without authentication by default.

If you need web access, add authentication:
```yaml
web_server:
  port: 80
  auth:
    username: admin
    password: !secret web_password
  local: true  # Only accessible from local network
```

### Secure Fallback AP

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  ap:
    ssid: "${device_name} Fallback"
    password: !secret fallback_ap_password

captive_portal:
```

**Why:** Open fallback AP allows anyone in range to access device configuration.

### Static IP Configuration

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  manual_ip:
    static_ip: 192.168.1.100
    gateway: 192.168.1.1
    subnet: 255.255.255.0
    dns1: 192.168.1.1
```

**Why:** Consistent IP makes firewall rules easier and prevents DHCP attacks.

---

## Network Security

### IoT VLAN Setup

Recommended network architecture:

```
┌─────────────────────────────────────────────────┐
│                    Router                        │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Main VLAN   │  │  IoT VLAN    │            │
│  │ 192.168.1.x  │  │ 192.168.10.x │            │
│  └──────────────┘  └──────────────┘            │
│         │                  │                    │
│    ┌────┴────┐      ┌─────┴─────┐              │
│    │   PCs   │      │   ESP32   │              │
│    │ Phones  │      │  Sensors  │              │
│    │   HA    │      │  Lights   │              │
│    └─────────┘      └───────────┘              │
└─────────────────────────────────────────────────┘
```

**VLAN Rules:**
- IoT devices: No internet access
- IoT devices: Can only communicate with Home Assistant IP
- IoT devices: Cannot communicate with each other (optional)
- Main VLAN: Can initiate connections to IoT VLAN

### Firewall Rules (Example for pfSense/OPNsense)

```
# Allow HA to reach IoT devices
pass from 192.168.1.50 to 192.168.10.0/24

# Allow IoT devices to respond to HA
pass from 192.168.10.0/24 to 192.168.1.50

# Block IoT internet access
block from 192.168.10.0/24 to any

# Block IoT cross-communication (optional)
block from 192.168.10.0/24 to 192.168.10.0/24
```

### DNS Blocking

Block ESPHome devices from resolving external domains:

```
# Unbound/Pi-hole local override
local-data: "esphome.io A 0.0.0.0"
local-data: "api.github.com A 0.0.0.0"
```

---

## MQTT Security

If using MQTT instead of native API:

```yaml
mqtt:
  broker: 192.168.1.50
  port: 8883  # TLS port
  username: !secret mqtt_user
  password: !secret mqtt_password
  certificate_authority: /config/certs/ca.crt
  client_certificate: /config/certs/client.crt
  client_key: /config/certs/client.key
```

**Mosquitto broker config:**
```
listener 8883
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key
require_certificate true
```

---

## Physical Security

### Tamper Detection

```yaml
binary_sensor:
  - platform: gpio
    pin:
      number: GPIO27
      mode: INPUT_PULLUP
    name: "Enclosure Tamper"
    device_class: tamper
    on_press:
      then:
        - logger.log: "ALERT: Enclosure opened!"
        # Optional: disable OTA temporarily
        - lambda: id(ota_component).set_auth_enabled(false);
```

### Disable UART/Debug After Deployment

```yaml
# Remove or disable in production:
# logger:
#   level: DEBUG
#   baud_rate: 115200

# Use minimal logging:
logger:
  level: WARN
  baud_rate: 0  # Disable UART output
```

---

## Secure Configuration Template

Complete security-hardened configuration:

```yaml
esphome:
  name: secure-device
  friendly_name: "Secure Device"

esp32:
  board: esp32dev

# Minimal logging in production
logger:
  level: WARN
  baud_rate: 0

# Encrypted API
api:
  encryption:
    key: !secret api_encryption_key

# Password-protected OTA
ota:
  - platform: esphome
    password: !secret ota_password

# Secure WiFi with fallback
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  fast_connect: true

  # Static IP for firewall rules
  manual_ip:
    static_ip: 192.168.10.100
    gateway: 192.168.10.1
    subnet: 255.255.255.0
    dns1: 192.168.10.1

  # Secure fallback AP
  ap:
    ssid: "Secure-Device-Fallback"
    password: !secret fallback_ap_password

# No web server in production
# web_server:

captive_portal:
```

---

## Security Audit Checklist

Run through this checklist before deploying:

```
□ secrets.yaml exists and contains all sensitive values
□ secrets.yaml is in .gitignore
□ API encryption key is unique (32 bytes, base64)
□ OTA password is set and strong
□ WiFi password uses WPA2/WPA3
□ Fallback AP has password set
□ Web server disabled or password-protected
□ Logger level set to WARN or higher
□ UART baud_rate set to 0
□ Static IP configured
□ Device on IoT VLAN (if available)
□ Firewall rules block internet access
□ Physical enclosure is secure
```

---

## Common Vulnerabilities

### Avoid These Mistakes

**Hardcoded credentials:**
```yaml
# BAD - Never do this!
wifi:
  ssid: "MyNetwork"
  password: "MyPassword123"

# GOOD - Use secrets
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
```

**Default/weak passwords:**
```yaml
# BAD
ota:
  password: "admin"

# GOOD
ota:
  password: !secret ota_password  # Use generated password
```

**Exposed web server:**
```yaml
# BAD - No authentication
web_server:
  port: 80

# BETTER - With auth (still not recommended for production)
web_server:
  port: 80
  auth:
    username: admin
    password: !secret web_password
```

**Debug logging in production:**
```yaml
# BAD - Exposes sensitive info
logger:
  level: VERBOSE

# GOOD - Minimal logging
logger:
  level: WARN
  baud_rate: 0
```

---

## Security Advisories

Notable security fixes by ESPHome release. If you operate any of the affected components, upgrading is recommended.

### 2026.5.0: DSMR missing GCM tag verification

**Component:** `dsmr` (Dutch Smart Meter Requirements, used by P1-port utility meters in the Netherlands, Belgium, and parts of Sweden)

**Issue:** Pre-2026.5.0 the DSMR parser decrypted incoming telegrams but did **not** verify the AES-GCM authentication tag. A malicious actor with access to the P1 serial line (or anything that could inject bytes onto it) could craft a payload that decrypts to attacker-controlled values without triggering a parse failure. Downstream consumers (HA energy dashboard, billing calculations, automations driven off meter readings) would receive forged data.

**Affected configurations:** any device using `dsmr:` with `decryption_key:` to read an encrypted smart meter, regardless of firmware version below 2026.5.0.

**Fix:** the 2026.5.0 DSMR rewrite (PR #15875) adds proper GCM tag verification. Telegrams with bad tags are now rejected at parse time. The rewrite also drops the Crypto-no-arduino dependency, eliminates dynamic allocations during parsing (saves ~1500 bytes per telegram), decrypts in place, fixes a potential event-loop hang, and adds several missing OBIS sensor mappings.

**Action:** upgrade to ESPHome 2026.5.0 or later. No YAML change is required - the fix is transparent. After upgrade, verify your meter still parses correctly (it should; encrypted meters with valid tags are unaffected).

### 2026.5.0: BLE coex behavior changed (not a vulnerability but worth noting)

The fix for `status=0x85` (133) GATT failures on bluetooth_proxy now holds `ESP_COEX_PREFER_BT` for the lifetime of any active BLE connection. This is the correct security/reliability tradeoff (lock operations now complete reliably) but means BLE-heavy configurations can deprioritize concurrent WiFi traffic. See [ble-proxy.md](ble-proxy.md) for details.

### 2026.6.0: ESP8266 min_auth_mode default raised to WPA2 (breaking)

On ESP8266 the default `min_auth_mode` under `wifi:` flipped from WPA to WPA2, matching the long-standing ESP32 default. Modern WPA2/WPA3 access points need no change. Only devices that must associate with a legacy WPA-only (TKIP) router are affected, and they need to pin the old behavior explicitly. PR #16682.

```yaml
wifi:
  min_auth_mode: WPA   # only needed for legacy WPA/TKIP routers on ESP8266
```

Raising the floor to WPA2 rejects weak TKIP-only association attempts, so leave it at the default unless an old router forces otherwise.

### 2026.6.0: WiFi SSIDs redacted in config output

`esphome config` now redacts WiFi SSIDs in addition to passwords, driven by `cv.sensitive()`. Pass `--show-secrets` when you genuinely need the resolved values (for example while debugging). PR #16690. This reduces the chance of leaking your network name when pasting config output into issues, chats, or screen shares.

Full 2026.6.0 details: references/release-2026-6.md

---

## See Also

- [secrets.yaml.example](../../examples/smart-garage/secrets.yaml.example) - Secrets template
- [generate_secrets.py](../../scripts/generate_secrets.py) - Key generation script
- [troubleshooting.md](troubleshooting.md) - Common issues
