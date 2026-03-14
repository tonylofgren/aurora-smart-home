# Energy & Electricity APIs

Covers Tibber, Nordpool (Energi Data Service), and Vattenfall open data.

---

## Tibber

**What it provides:** Real-time electricity price (your personal tariff including grid fees), hourly
price forecast, energy consumption from Tibber Pulse, cost history.

**Auth:** Bearer token — personal access token from developer.tibber.com
**Protocol:** GraphQL over HTTPS
**Base URL:** `https://api.tibber.com/v1-beta/gql`
**Rate limit:** ~1 req/s, practical: poll every 60s is fine
**Requires:** Tibber subscription (Sweden, Norway, Germany, Netherlands)

### Get your token
1. Go to [developer.tibber.com](https://developer.tibber.com)
2. Sign in with your Tibber account
3. Copy the Personal Access Token

### Key queries

**Current price:**
```graphql
{
  viewer {
    homes {
      currentSubscription {
        priceInfo {
          current {
            total
            energy
            tax
            startsAt
            currency
            level
          }
        }
      }
    }
  }
}
```

**Today's + tomorrow's hourly prices:**
```graphql
{
  viewer {
    homes {
      currentSubscription {
        priceInfo {
          today { total startsAt level }
          tomorrow { total startsAt level }
        }
      }
    }
  }
}
```

**Consumption (last 24 hours):**
```graphql
{
  viewer {
    homes {
      consumption(resolution: HOURLY, last: 24) {
        nodes { from to cost unitCost unitPrice consumption }
      }
    }
  }
}
```

### Node-RED implementation

```
[inject: every 60s]
  → [function: build GraphQL request]
  → [http request: POST tibber API]
  → [function: extract price]
  → [api-call-service: set input_number.electricity_price]
```

**Function node — build request:**
```javascript
msg.payload = JSON.stringify({
    query: `{
        viewer {
            homes {
                currentSubscription {
                    priceInfo {
                        current { total level startsAt currency }
                    }
                }
            }
        }
    }`
});
msg.headers = {
    "Authorization": "Bearer " + env.get("TIBBER_TOKEN"),
    "Content-Type": "application/json"
};
return msg;
```

**HTTP request node config:**
```json
{
  "type": "http request",
  "method": "POST",
  "url": "https://api.tibber.com/v1-beta/gql",
  "ret": "obj"
}
```

**Function node — extract and route:**
```javascript
const price = msg.payload.data.viewer.homes[0]
    .currentSubscription.priceInfo.current;

// Push to HA
msg.payload = {
    action: "input_number.set_value",
    target: { entity_id: "input_number.electricity_price" },
    data: { value: price.total }
};

// Also set a price level attribute
flow.set("priceLevel", price.level); // VERY_CHEAP, CHEAP, NORMAL, EXPENSIVE, VERY_EXPENSIVE
return msg;
```

**Store API token in Node-RED:**
Node-RED → Menu → Manage Palette → Environment Variables, or add to `settings.js`:
```javascript
process.env.TIBBER_TOKEN = "your-token-here";
```

### HA YAML REST sensor

```yaml
# configuration.yaml
rest:
  - scan_interval: 60
    resource: https://api.tibber.com/v1-beta/gql
    method: POST
    headers:
      Authorization: !secret tibber_token
      Content-Type: application/json
    payload: '{"query": "{ viewer { homes { currentSubscription { priceInfo { current { total level startsAt currency } } } } } }"}'
    sensor:
      - name: "Electricity Price"
        unique_id: tibber_current_price
        value_template: "{{ value_json.data.viewer.homes[0].currentSubscription.priceInfo.current.total }}"
        unit_of_measurement: "SEK/kWh"
        device_class: monetary
        state_class: measurement
      - name: "Price Level"
        unique_id: tibber_price_level
        value_template: "{{ value_json.data.viewer.homes[0].currentSubscription.priceInfo.current.level }}"
```

```yaml
# secrets.yaml
tibber_token: "Bearer eyJhbG..."
```

### Full HACS integration

Use the `ha-integration` skill with this prompt:
```
Create a Home Assistant integration for the Tibber API.
Auth: Bearer token. Key entities:
- sensor.tibber_current_price (SEK/kWh, state_class: measurement)
- sensor.tibber_price_level (VERY_CHEAP/CHEAP/NORMAL/EXPENSIVE/VERY_EXPENSIVE)
- sensor.tibber_cost_today (SEK)
- sensor.tibber_consumption_today (kWh)
Poll current price every 60 seconds. Fetch today's price list hourly.
HACS-ready. GitHub: myuser.
```

---

## Nordpool via Energi Data Service

**What it provides:** Wholesale Nordpool spot prices (no personal tariff — raw market price),
hourly for all Nordic/Baltic price areas. Free, public, no API key needed.

**Auth:** None
**Base URL:** `https://api.energidataservice.dk/dataset/Elspotprices`
**Rate limit:** None stated, be polite — poll at most every 5 minutes
**Price areas:** SE1, SE2, SE3, SE4 (Sweden), NO1–NO5 (Norway), DK1, DK2, FI

### Key endpoints

**Today's and tomorrow's prices for SE3:**
```
GET https://api.energidataservice.dk/dataset/Elspotprices
  ?start=now/P1D
  &end=now%2BP2D
  &filter={"PriceArea":"SE3"}
  &sort=HourDK asc
  &columns=HourDK,SpotPriceDKK,SpotPriceEUR
```

**Response:**
```json
{
  "records": [
    {
      "HourDK": "2026-03-14T00:00:00",
      "SpotPriceDKK": 45.67,
      "SpotPriceEUR": 4.34
    }
  ]
}
```

> Note: Price is in DKK/MWh or EUR/MWh. Convert to SEK/kWh:
> `SpotPriceDKK / 1000 * [DKK→SEK rate]` or use EUR: `SpotPriceEUR / 1000 * [EUR→SEK rate]`

### Node-RED flow

```
[inject: every hour at :00]
  → [http request: GET energidataservice.dk]
  → [function: extract current hour price + build forecast]
  → [api-call-service: set input_number + notify if spike]
```

**Function node — extract current price:**
```javascript
const records = msg.payload.records;
const now = new Date();
const currentHour = now.toISOString().slice(0, 13);

const current = records.find(r => r.HourDK.startsWith(currentHour));
if (!current) { node.warn("No price for current hour"); return null; }

// Convert DKK/MWh to SEK/kWh (approx 1 DKK = 1.6 SEK)
const priceKWh = (current.SpotPriceDKK / 1000 * 1.6).toFixed(4);

msg.payload = {
    action: "input_number.set_value",
    target: { entity_id: "input_number.nordpool_price" },
    data: { value: parseFloat(priceKWh) }
};
return msg;
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 3600
    resource: "https://api.energidataservice.dk/dataset/Elspotprices?start=now/P1D&end=now%2BP2D&filter=%7B%22PriceArea%22%3A%22SE3%22%7D&sort=HourDK+asc"
    sensor:
      - name: "Nordpool Price SE3"
        unique_id: nordpool_price_se3
        value_template: >-
          {% set records = value_json.records %}
          {% set now_hour = now().strftime('%Y-%m-%dT%H') %}
          {% set rec = records | selectattr('HourDK', 'search', now_hour) | first %}
          {{ (rec.SpotPriceDKK / 1000 * 1.6) | round(4) }}
        unit_of_measurement: "SEK/kWh"
        state_class: measurement
```

> **Tip:** The community integration [nordpool](https://github.com/custom-components/nordpool) on HACS
> handles this automatically with proper currency conversion. Recommend it over DIY for most users.

---

## Vattenfall Open Data

**What it provides:** Swedish grid data, historical consumption, carbon intensity.
**Auth:** None (public datasets)
**Base URL:** `https://www.vattenfall.se/api/` (limited) or via ENTSO-E Transparency Platform

> For most use cases, the Nordpool/Energi Data Service approach above is more practical.
> For grid carbon intensity, use the **Electricity Maps** API instead (electricitymaps.com).

---

## Electricity Maps (Carbon Intensity)

**What it provides:** Real-time carbon intensity of the electricity grid by zone (gCO2eq/kWh),
renewable percentage, fossil-free percentage. Perfect for "green automations".

**Auth:** API key in header
**Base URL:** `https://api.electricitymap.org/v3`
**Free tier:** 1 zone, 1 request/hour
**Get key:** electricitymap.org → Sign up → Free tier

### Endpoint

```
GET https://api.electricitymap.org/v3/carbon-intensity/latest?zone=SE
Headers: auth-token: {your-api-key}
```

**Response:**
```json
{
  "zone": "SE",
  "carbonIntensity": 28,
  "datetime": "2026-03-14T10:00:00.000Z",
  "fossilFreePercentage": 97,
  "renewablePercentage": 75
}
```

### HA YAML

```yaml
rest:
  - scan_interval: 3600
    resource: https://api.electricitymap.org/v3/carbon-intensity/latest?zone=SE
    headers:
      auth-token: !secret electricity_maps_key
    sensor:
      - name: "Grid Carbon Intensity"
        value_template: "{{ value_json.carbonIntensity }}"
        unit_of_measurement: "gCO2eq/kWh"
      - name: "Fossil Free Percentage"
        value_template: "{{ value_json.fossilFreePercentage }}"
        unit_of_measurement: "%"
```
