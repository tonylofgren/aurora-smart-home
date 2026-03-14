# Popular APIs — Node-RED Quick Reference

Quick reference for connecting external APIs in Node-RED flows. For deep documentation on each
API (auth setup, response schemas, HA YAML sensors), see the `api-catalog` skill.

---

## HTTP Request Node Patterns

### GET with API key in URL
```json
{
  "type": "http request",
  "method": "GET",
  "url": "https://api.example.com/data?apikey={{env.MY_KEY}}",
  "ret": "obj"
}
```

### POST with Bearer token
```json
{
  "type": "http request",
  "method": "POST",
  "url": "https://api.example.com/endpoint",
  "headers": {
    "Authorization": "Bearer {{env.API_TOKEN}}",
    "Content-Type": "application/json"
  },
  "ret": "obj"
}
```

---

## Energy APIs

### Tibber — current electricity price
```javascript
// Function: build request
msg.payload = JSON.stringify({
    query: "{ viewer { homes { currentSubscription { priceInfo { current { total level } } } } } }"
});
msg.headers = {
    "Authorization": "Bearer " + env.get("TIBBER_TOKEN"),
    "Content-Type": "application/json"
};
return msg;
// HTTP node: POST https://api.tibber.com/v1-beta/gql
```

### Nordpool — spot price SE3
```javascript
// HTTP GET: https://api.energidataservice.dk/dataset/Elspotprices?start=now/P1D&end=now%2BP2D&filter={"PriceArea":"SE3"}&sort=HourDK asc
const records = msg.payload.records;
const hour = new Date().toISOString().slice(0, 13);
const rec = records.find(r => r.HourDK.startsWith(hour));
msg.payload = rec ? (rec.SpotPriceDKK / 1000 * 1.6).toFixed(4) : null;
return msg;
```

---

## Weather APIs

### SMHI — Stockholm forecast (no auth)
```javascript
// HTTP GET: https://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/18.0686/lat/59.3293/data.json
const series = msg.payload.timeSeries;
const now = new Date();
const current = series.reduce((prev, curr) =>
    Math.abs(new Date(curr.validTime) - now) < Math.abs(new Date(prev.validTime) - now) ? curr : prev
);
const getP = (name) => current.parameters.find(p => p.name === name)?.values[0];
msg.payload = { temp: getP("t"), humidity: getP("r"), wind: getP("ws"), symbol: getP("Wsymb2") };
return msg;
```

### OpenWeatherMap — One Call API
```javascript
// HTTP GET: https://api.openweathermap.org/data/3.0/onecall?lat=59.33&lon=18.07&units=metric&lang=sv&appid={{env.OWM_KEY}}
const c = msg.payload.current;
msg.payload = { temp: c.temp, humidity: c.humidity, wind: c.wind_speed, desc: c.weather[0].description };
return msg;
```

### yr.no — Oslo (no auth, User-Agent required)
```javascript
// Function: set required header
msg.headers = { "User-Agent": "MyHomeAutomation/1.0 you@email.com" };
// HTTP GET: https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=59.91&lon=10.75
const d = msg.payload.properties.timeseries[0].data;
msg.payload = { temp: d.instant.details.air_temperature, symbol: d.next_1_hours?.summary?.symbol_code };
return msg;
```

---

## Transport APIs

### SL — Stockholm departures (no auth)
```javascript
// HTTP GET: https://transport.integration.sl.se/v1/sites/9001/departures?forecast=30
const deps = msg.payload.departures;
const myLine = "14";
const next = deps.filter(d => d.line.designation === myLine).slice(0, 3)
    .map(d => Math.round((new Date(d.expected) - new Date()) / 60000) + " min");
msg.payload = next.join(", ") || "No departures";
return msg;
```

### Trafikverket — train delays
```javascript
// Function: build request body
msg.payload = JSON.stringify({ REQUEST: { LOGIN: { id: env.get("TRAFIKVERKET_KEY") },
    QUERY: [{ OBJECTTYPE: "TrainAnnouncement", FILTER: { AND: [
        { EQ: { name: "LocationSignature", value: "Cst" } },
        { EQ: { name: "ActivityType", value: "Avgang" } },
        { GT: { name: "AdvertisedTimeAtLocation", value: "$dateadd(-00:05:00)" } },
        { LT: { name: "AdvertisedTimeAtLocation", value: "$dateadd(02:00:00)" } }
    ]}, INCLUDE: ["AdvertisedTimeAtLocation", "ToLocation", "Delay", "Canceled"] }] }});
msg.headers = { "Content-Type": "application/json" };
return msg;
// HTTP node: POST https://api.trafikverket.se/v2/data.json
```

### Entur — Oslo S departures (Norway, no auth)
```javascript
// Function: build GraphQL request
msg.payload = JSON.stringify({ query: `{
    stopPlace(id: "NSR:StopPlace:337") {
        estimatedCalls(timeRange: 3600, numberOfDepartures: 3) {
            expectedDepartureTime
            destinationDisplay { frontText }
            serviceJourney { journeyPattern { line { publicCode } } }
        }
    }
}` });
msg.headers = { "Content-Type": "application/json", "ET-Client-Name": "my-home-assistant" };
return msg;
// HTTP node: POST https://api.entur.io/journey-planner/v3/graphql
```

---

## Smart Home Clouds

### Shelly — local control (Gen1)
```javascript
// HTTP GET: http://192.168.1.100/relay/0?turn=on   (no auth by default)
// HTTP GET: http://192.168.1.100/relay/0?turn=off
// HTTP GET: http://192.168.1.100/status            (full status)
const isOn = msg.payload.relays[0].ison;
const power = msg.payload.meters?.[0]?.power;
```

### Shelly Gen2+ (RPC)
```javascript
// HTTP POST: http://{ip}/rpc/Switch.Set
msg.payload = JSON.stringify({ id: 0, on: true });
// HTTP POST: http://{ip}/rpc/Switch.GetStatus
msg.payload = JSON.stringify({ id: 0 });
```

### Philips Hue — local bridge
```javascript
// HTTP PUT: http://{bridge-ip}/api/{username}/lights/{id}/state
msg.method = "PUT";
msg.url = `http://192.168.1.50/api/${env.get("HUE_USERNAME")}/lights/1/state`;
msg.payload = JSON.stringify({ on: true, bri: 200, ct: 370 });
```

### Philips Hue — activate scene
```javascript
// HTTP PUT: /api/{username}/groups/{id}/action
msg.payload = JSON.stringify({ scene: "scene-id" });
```

---

## Global APIs

### OpenAI — GPT chat
```javascript
// Function: build chat request
msg.payload = JSON.stringify({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: msg.payload }],
    max_tokens: 150
});
msg.headers = { "Authorization": "Bearer " + env.get("OPENAI_KEY"), "Content-Type": "application/json" };
return msg;
// HTTP node: POST https://api.openai.com/v1/chat/completions

// Parse response:
msg.payload = msg.payload.choices[0].message.content;
```

### Spotify — playback control
```javascript
// Play/pause
msg.method = "PUT";
msg.url = "https://api.spotify.com/v1/me/player/play"; // or /pause
msg.headers = { "Authorization": "Bearer " + flow.get("spotifyToken") };
msg.payload = ""; // empty body for play/pause
return msg;
```

```javascript
// Current track
// HTTP GET: https://api.spotify.com/v1/me/player/currently-playing
const item = msg.payload.item;
msg.payload = item ? `${item.name} — ${item.artists[0].name}` : "Nothing playing";
return msg;
```

### Telegram — send message
```javascript
// Function: send Telegram message
msg.method = "POST";
msg.url = `https://api.telegram.org/bot${env.get("TELEGRAM_TOKEN")}/sendMessage`;
msg.payload = JSON.stringify({
    chat_id: env.get("TELEGRAM_CHAT_ID"),
    text: msg.payload,
    parse_mode: "HTML"
});
msg.headers = { "Content-Type": "application/json" };
return msg;
```

### Telegram — send photo
```javascript
msg.url = `https://api.telegram.org/bot${env.get("TELEGRAM_TOKEN")}/sendPhoto`;
msg.payload = JSON.stringify({
    chat_id: env.get("TELEGRAM_CHAT_ID"),
    photo: "https://your-camera-snapshot-url",
    caption: "Motion detected at front door"
});
```

### GitHub — latest release check
```javascript
// HTTP GET: https://api.github.com/repos/{owner}/{repo}/releases/latest
// Headers: Authorization: Bearer {token}, Accept: application/vnd.github+json
const latest = msg.payload.tag_name;
const current = flow.get("currentVersion");
if (latest !== current) {
    node.warn(`Update available: ${latest}`);
}
```

### Google Calendar — check current events
```javascript
// HTTP GET: https://www.googleapis.com/calendar/v3/calendars/primary/events
// ?maxResults=5&singleEvents=true&orderBy=startTime&timeMin={now ISO}
// Headers: Authorization: Bearer {token}
const now = new Date();
const inMeeting = (msg.payload.items || []).some(e => {
    const start = new Date(e.start.dateTime || e.start.date);
    const end = new Date(e.end.dateTime || e.end.date);
    return start <= now && end >= now;
});
msg.payload = inMeeting;
return msg;
```

---

## Env Variable Storage

Store all API keys in Node-RED environment variables — never hardcode them in function nodes:

**Node-RED → Settings → Environment Variables:**
```
TIBBER_TOKEN     = eyJhbG...
OWM_KEY          = abc123...
TELEGRAM_TOKEN   = 1234567890:ABC...
TELEGRAM_CHAT_ID = 123456789
OPENAI_KEY       = sk-...
GITHUB_TOKEN     = github_pat_...
HUE_USERNAME     = abc123def456...
TRAFIKVERKET_KEY = your-key-here
```

Or in `settings.js`:
```javascript
process.env.TIBBER_TOKEN = "...";
```

Access in function nodes with `env.get("TIBBER_TOKEN")`.
