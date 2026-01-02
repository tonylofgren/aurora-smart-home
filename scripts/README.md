# Aurora Smart Home Scripts

Helper scripts for working with ESPHome and Home Assistant configurations.

## generate_secrets

Generates secure secrets for ESPHome configurations.

### Python Version (Cross-platform)

```bash
# Print secrets to console
python scripts/generate_secrets.py

# Create secrets.yaml file
python scripts/generate_secrets.py --output

# Create with custom filename
python scripts/generate_secrets.py -o my_secrets.yaml

# Include WiFi credentials
python scripts/generate_secrets.py --output --wifi-ssid "MyNetwork" --wifi-password "MyPassword"

# Get just an API key
python scripts/generate_secrets.py --api-key-only
```

### Bash Version (Linux/Mac)

```bash
# Make executable
chmod +x scripts/generate_secrets.sh

# Print secrets to console
./scripts/generate_secrets.sh

# Create secrets.yaml file
./scripts/generate_secrets.sh --output

# Create with custom filename
./scripts/generate_secrets.sh -o my_secrets.yaml

# Get just an API key
./scripts/generate_secrets.sh --api-key-only
```

## Generated Secrets

The scripts generate:

| Secret | Format | Used For |
|--------|--------|----------|
| `api_encryption_key` | 32 bytes, base64 | Secure HA communication |
| `ota_password` | 12 chars, URL-safe | OTA updates |
| `ap_password` | 8 hex chars | Fallback AP |

## Example Output

```yaml
# secrets.yaml
wifi_ssid: "YOUR_WIFI_SSID"
wifi_password: "YOUR_WIFI_PASSWORD"
api_encryption_key: "dGVzdGtleXRlc3RrZXl0ZXN0a2V5dGVzdGtleXRlcw=="
ota_password: "xK9mN2pQr4sT"
ap_password: "a1b2c3d4"
```

## Security Notes

- **Never commit secrets.yaml to git!**
- Add `secrets.yaml` to your `.gitignore`
- Each device should use unique secrets
- Store backups securely

## Usage in ESPHome

```yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
  encryption:
    key: !secret api_encryption_key

ota:
  password: !secret ota_password
```
