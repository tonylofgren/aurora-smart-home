# Weather APIs

Covers SMHI, OpenWeatherMap, yr.no, and Tomorrow.io.

---

## SMHI Open Data (Sweden)

**What it provides:** Official Swedish meteorological data - current conditions, 10-day forecast,
warnings, historical data. Highest accuracy for Sweden.

**Auth:** None - completely free and public
**Base URL:** `https://opendata-download-metfcst.smhi.se/api`
**Rate limit:** None stated, reasonable use expected
**Coverage:** Sweden only

### Key endpoints

**10-day point forecast:**
```
GET https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/{lon}/lat/{lat}/data.json
```

Replace `{lon}` and `{lat}` with your coordinates (e.g., Stockholm: lon=18.0686, lat=59.3293).

**Weather parameters (key ones):**

| Parameter | Description | Unit |
|-----------|-------------|------|
| `t` | Air temperature | °C |
| `r` | Relative humidity | % |
| `ws` | Wind speed | m/s |
| `wd` | Wind direction | degrees |
| `prec1h` | Precipitation last hour | mm |
| `pcat` | Precipitation category (0=none, 1=snow, 2=snow+rain, 3=rain, 4=drizzle, 5=freezing rain, 6=freezing drizzle) | - |
| `Wsymb2` | Weather symbol (1=clear sky, 2=nearly clear, ... 27=thunderstorm) | - |
| `vis` | Visibility | km |
| `gust` | Wind gust speed | m/s |

**Response structure:**
```json
{
  "timeSeries": [
    {
      "validTime": "2026-03-14T11:00:00Z",
      "parameters": [
        {"name": "t", "values": [3.2]},
        {"name": "prec1h", "values": [0.0]},
        {"name": "Wsymb2", "values": [2]}
      ]
    }
  ]
}
```

### Node-RED implementation

```
[inject: every 30 min]
  → [http request: GET smhi forecast]
  → [function: extract current hour + nearest future values]
  → [api-call-service: update HA sensors]
```

**Function node - extract current conditions:**
```javascript
const series = msg.payload.timeSeries;
const now = new Date();

// Find the timeSeries entry closest to now (SMHI gives hourly)
const current = series.reduce((prev, curr) => {
    const prevDiff = Math.abs(new Date(prev.validTime) - now);
    const currDiff = Math.abs(new Date(curr.validTime) - now);
    return currDiff < prevDiff ? curr : prev;
});

function getParam(params, name) {
    const p = params.find(p => p.name === name);
    return p ? p.values[0] : null;
}

const params = current.parameters;
const weather = {
    temperature: getParam(params, "t"),
    humidity: getParam(params, "r"),
    wind_speed: getParam(params, "ws"),
    precipitation: getParam(params, "prec1h"),
    symbol: getParam(params, "Wsymb2")
};

// Send to HA via api-call-service for each sensor
msg.weather = weather;
return msg;
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 1800
    resource: "https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.0686/lat/59.3293/data.json"
    sensor:
      - name: "SMHI Temperature"
        unique_id: smhi_temperature
        value_template: >-
          {% set now = utcnow().replace(minute=0, second=0, microsecond=0) %}
          {% set series = value_json.timeSeries %}
          {% set current = series | selectattr('validTime', 'ge', now.strftime('%Y-%m-%dT%H:%M:%SZ')) | first %}
          {{ current.parameters | selectattr('name', 'eq', 't') | map(attribute='values') | first | first }}
        unit_of_measurement: "°C"
        device_class: temperature
        state_class: measurement
      - name: "SMHI Precipitation"
        unique_id: smhi_precipitation
        value_template: >-
          {% set series = value_json.timeSeries %}
          {% set first = series | first %}
          {{ first.parameters | selectattr('name', 'eq', 'prec1h') | map(attribute='values') | first | first }}
        unit_of_measurement: "mm"
```

> **Tip:** For simple weather display, the built-in SMHI integration in Home Assistant is often easier.
> Use the REST approach only when you need specific data not exposed by the integration.

---

## OpenWeatherMap

**What it provides:** Global weather data - current conditions, 5-day forecast, air quality, UV index,
historical data. Widely used, good global coverage.

**Auth:** API key in URL parameter (`appid`)
**Base URL:** `https://api.openweathermap.org/data/3.0`
**Free tier:** 1,000 calls/day, 60 calls/min (One Call API 3.0)
**Get key:** openweathermap.org → Sign up → API keys (takes ~2 hours to activate)

### Key endpoints

**Current weather + 48h hourly + 8-day daily (One Call API 3.0):**
```
GET https://api.openweathermap.org/data/3.0/onecall
  ?lat=59.3293&lon=18.0686
  &appid={API_KEY}
  &units=metric
  &lang=sv
  &exclude=minutely,alerts
```

**Air quality index:**
```
GET https://api.openweathermap.org/data/2.5/air_pollution
  ?lat=59.3293&lon=18.0686
  &appid={API_KEY}
```

**Response (One Call, simplified):**
```json
{
  "current": {
    "temp": 3.2,
    "feels_like": -0.5,
    "humidity": 72,
    "uvi": 0.3,
    "wind_speed": 4.1,
    "weather": [{"description": "molnigt", "icon": "04d"}]
  },
  "hourly": [
    {"dt": 1710410400, "temp": 3.0, "pop": 0.2, "rain": {"1h": 0.15}}
  ],
  "daily": [
    {"dt": 1710374400, "temp": {"day": 4.1, "min": 1.2, "max": 6.3}, "pop": 0.4}
  ]
}
```

### Node-RED implementation

**HTTP request node:**
```json
{
  "type": "http request",
  "method": "GET",
  "url": "https://api.openweathermap.org/data/3.0/onecall?lat=59.3293&lon=18.0686&units=metric&lang=sv&appid={{env.OWM_API_KEY}}",
  "ret": "obj"
}
```

**Function node - extract key values:**
```javascript
const c = msg.payload.current;
const tomorrow = msg.payload.daily[1]; // [0] is today

flow.set("weather", {
    temp: c.temp,
    feels_like: c.feels_like,
    humidity: c.humidity,
    wind_speed: c.wind_speed,
    description: c.weather[0].description,
    rain_tomorrow_chance: Math.round(tomorrow.pop * 100),
    temp_max_tomorrow: tomorrow.temp.max,
    temp_min_tomorrow: tomorrow.temp.min
});

// Check for rain tomorrow
if (tomorrow.pop > 0.5) {
    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "Weather tomorrow",
            message: `Rain likely (${Math.round(tomorrow.pop*100)}%). Pack an umbrella.`
        }
    };
    return msg;
}
return null;
```

### HA YAML REST sensor

```yaml
# secrets.yaml
owm_api_key: "your_api_key_here"
```

```yaml
rest:
  - scan_interval: 600
    resource_template: "https://api.openweathermap.org/data/3.0/onecall?lat=59.3293&lon=18.0686&units=metric&lang=sv&exclude=minutely&appid={{ states('input_text.owm_api_key') }}"
    sensor:
      - name: "OWM Temperature"
        value_template: "{{ value_json.current.temp }}"
        unit_of_measurement: "°C"
        device_class: temperature
      - name: "OWM Humidity"
        value_template: "{{ value_json.current.humidity }}"
        unit_of_measurement: "%"
        device_class: humidity
      - name: "OWM Wind Speed"
        value_template: "{{ value_json.current.wind_speed }}"
        unit_of_measurement: "m/s"
      - name: "OWM Rain Chance Tomorrow"
        value_template: "{{ (value_json.daily[1].pop * 100) | int }}"
        unit_of_measurement: "%"
      - name: "OWM Description"
        value_template: "{{ value_json.current.weather[0].description }}"
```

> **Simpler alternative:** Home Assistant has a built-in OpenWeatherMap integration.
> Use the REST approach only if you need data not exposed by the official integration.

---

## yr.no (Norway/Nordic)

**What it provides:** Official Norwegian meteorological forecast. Excellent for Norway and Nordic
countries, free, no API key.

**Auth:** Must include `User-Agent` header (required by their ToS)
**Base URL:** `https://api.met.no/weatherapi`
**Rate limit:** Cache responses for at least 30 minutes (check `Expires` header)
**Coverage:** Global, best for Nordic countries

### Key endpoint

**Compact 9-day forecast:**
```
GET https://api.met.no/weatherapi/locationforecast/2.0/compact
  ?lat=59.9139&lon=10.7522
Headers:
  User-Agent: MyHomeAutomation/1.0 contact@myemail.com
```

**Response:**
```json
{
  "properties": {
    "timeseries": [
      {
        "time": "2026-03-14T11:00:00Z",
        "data": {
          "instant": {
            "details": {
              "air_temperature": 5.1,
              "relative_humidity": 68.4,
              "wind_speed": 3.2,
              "precipitation_rate": 0.0
            }
          },
          "next_1_hours": {
            "summary": {"symbol_code": "partlycloudy_day"},
            "details": {"precipitation_amount": 0.0}
          }
        }
      }
    ]
  }
}
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 1800
    resource: "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.9139&lon=10.7522"
    headers:
      User-Agent: "HomeAssistant/1.0 your@email.com"
    sensor:
      - name: "yr.no Temperature"
        value_template: "{{ value_json.properties.timeseries[0].data.instant.details.air_temperature }}"
        unit_of_measurement: "°C"
        device_class: temperature
      - name: "yr.no Wind Speed"
        value_template: "{{ value_json.properties.timeseries[0].data.instant.details.wind_speed }}"
        unit_of_measurement: "m/s"
      - name: "yr.no Symbol"
        value_template: "{{ value_json.properties.timeseries[0].data.next_1_hours.summary.symbol_code }}"
```

---

## Tomorrow.io

**What it provides:** High-resolution weather forecasts, hyperlocal, good for automations needing
precise precipitation timing. Free tier available.

**Auth:** API key in URL (`apikey` parameter)
**Base URL:** `https://api.tomorrow.io/v4`
**Free tier:** 500 calls/day, 25 calls/hour
**Get key:** tomorrow.io → Sign up → API Key

### Key endpoint

**Real-time weather:**
```
GET https://api.tomorrow.io/v4/weather/realtime
  ?location=59.3293,18.0686
  &apikey={API_KEY}
  &units=metric
```

**Hourly forecast (next 24h):**
```
GET https://api.tomorrow.io/v4/weather/forecast
  ?location=59.3293,18.0686
  &timesteps=1h
  &apikey={API_KEY}
  &units=metric
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 600
    resource: "https://api.tomorrow.io/v4/weather/realtime?location=59.3293,18.0686&units=metric&apikey=YOUR_KEY"
    sensor:
      - name: "Tomorrow.io Temperature"
        value_template: "{{ value_json.data.values.temperature }}"
        unit_of_measurement: "°C"
        device_class: temperature
      - name: "Tomorrow.io Rain Intensity"
        value_template: "{{ value_json.data.values.rainIntensity }}"
        unit_of_measurement: "mm/h"
      - name: "Tomorrow.io UV Index"
        value_template: "{{ value_json.data.values.uvIndex }}"
```
