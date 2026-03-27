# Transport APIs

Covers SL (Stockholm), Trafikverket, Resrobot (national Sweden), and Entur (Norway).

---

## SL - Stockholms Lokaltrafik

**What it provides:** Real-time departures, journey planning, disruptions for Stockholm public transit.

**Auth:** API key in header
**Base URL:** `https://transport.integration.sl.se/v1`
**Get key:** sl.se/api → Register → API key (free)
**Rate limit:** 10,000 req/day (free tier)

### Find your stop ID

First you need the stop's `gid` (Globalt ID):
```
GET https://journeyplanner.integration.sl.se/v1/stop-areas/?q=T-Centralen
Headers: Content-Type: application/json
```

Common Stockholm stops:
- T-Centralen: `9001`
- Stockholm City: `9180`
- Slussen: `9192`

### Get real-time departures

```
GET https://transport.integration.sl.se/v1/sites/{stop_gid}/departures
  ?forecast=30
Headers: (no API key needed for departures endpoint since 2024!)
```

**Response:**
```json
{
  "departures": [
    {
      "direction": "Mörby centrum",
      "state": "EXPECTED",
      "expected": "2026-03-14T10:23:00",
      "scheduled": "2026-03-14T10:22:00",
      "line": {"designation": "14", "transport_mode": "METRO", "name": "tunnelbana"},
      "stop_area": {"name": "T-Centralen"}
    }
  ]
}
```

### Node-RED implementation

```
[inject: every 2 min]
  → [http request: GET departures]
  → [function: extract next 3 departures for my line]
  → [api-call-service: update sensor.next_bus]
```

**Function node - extract next departures for line 42:**
```javascript
const departures = msg.payload.departures;
const myLine = "42"; // Change to your line

const filtered = departures
    .filter(d => d.line.designation === myLine)
    .slice(0, 3)
    .map(d => {
        const expected = new Date(d.expected);
        const now = new Date();
        const minutes = Math.round((expected - now) / 60000);
        return `${minutes} min`;
    });

msg.payload = {
    action: "input_text.set_value",
    target: { entity_id: "input_text.next_bus_42" },
    data: { value: filtered.join(", ") || "No departures" }
};
return msg;
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 120
    resource: "https://transport.integration.sl.se/v1/sites/9001/departures?forecast=30"
    sensor:
      - name: "SL Next Departure Line 14"
        value_template: >-
          {% set deps = value_json.departures | selectattr('line.designation', 'eq', '14') | list %}
          {% if deps %}
            {% set next = deps[0] %}
            {% set t = next.expected | as_datetime %}
            {{ ((t - now()) / 60) | int }} min
          {% else %}
            No data
          {% endif %}
```

---

## Trafikverket Open API

**What it provides:** Swedish national train departures/arrivals (all operators), train delays,
road traffic, weather stations on roads, camera images, infrastructure data.

**Auth:** API key in XML request body (SOAP-style) or REST (newer endpoints)
**Base URL:** `https://api.trafikverket.se/v2/data.json`
**Get key:** trafikverket.se/api → Register → Free API key
**Rate limit:** 10,000 req/10 min

### Train departures (REST-style)

```
POST https://api.trafikverket.se/v2/data.json
Headers:
  Content-Type: application/json
Body:
{
  "REQUEST": {
    "LOGIN": {"id": "YOUR_API_KEY"},
    "QUERY": [{
      "OBJECTTYPE": "TrainAnnouncement",
      "FILTER": {
        "AND": [
          {"EQ": {"name": "LocationSignature", "value": "Cst"}},
          {"EQ": {"name": "ActivityType", "value": "Avgang"}},
          {"GT": {"name": "AdvertisedTimeAtLocation", "value": "$dateadd(-00:30:00)"}},
          {"LT": {"name": "AdvertisedTimeAtLocation", "value": "$dateadd(02:00:00)"}}
        ]
      },
      "INCLUDE": [
        "AdvertisedTimeAtLocation",
        "EstimatedTimeAtLocation",
        "ToLocation",
        "TrainOwner",
        "Delay",
        "Canceled"
      ]
    }]
  }
}
```

**Common station codes:** Cst (Stockholm Central), G (Gothenburg), M (Malmö), U (Uppsala)

**Response:**
```json
{
  "RESPONSE": {
    "RESULT": [{
      "TrainAnnouncement": [
        {
          "AdvertisedTimeAtLocation": "2026-03-14T10:45:00",
          "EstimatedTimeAtLocation": "2026-03-14T10:52:00",
          "ToLocation": [{"LocationName": "G"}],
          "Delay": "PT7M",
          "Canceled": false
        }
      ]
    }]
  }
}
```

### Node-RED implementation

```javascript
// Function node - build Trafikverket request
msg.payload = JSON.stringify({
    REQUEST: {
        LOGIN: { id: env.get("TRAFIKVERKET_KEY") },
        QUERY: [{
            OBJECTTYPE: "TrainAnnouncement",
            FILTER: {
                AND: [
                    { EQ: { name: "LocationSignature", value: "Cst" } },
                    { EQ: { name: "ActivityType", value: "Avgang" } },
                    { GT: { name: "AdvertisedTimeAtLocation", value: "$dateadd(-00:05:00)" } },
                    { LT: { name: "AdvertisedTimeAtLocation", value: "$dateadd(02:00:00)" } }
                ]
            },
            INCLUDE: ["AdvertisedTimeAtLocation", "EstimatedTimeAtLocation",
                      "ToLocation", "Delay", "Canceled"]
        }]
    }
});
msg.headers = { "Content-Type": "application/json" };
return msg;
```

**HTTP request node:**
```json
{
  "method": "POST",
  "url": "https://api.trafikverket.se/v2/data.json",
  "ret": "obj"
}
```

**Function node - extract delays:**
```javascript
const trains = msg.payload.RESPONSE.RESULT[0].TrainAnnouncement || [];
const delayed = trains.filter(t => t.Delay && t.Delay !== "PT0S");

if (delayed.length > 0) {
    const first = delayed[0];
    const dest = first.ToLocation[0].LocationName;
    // PT7M → 7 minutes
    const delayMin = parseInt(first.Delay.replace("PT", "").replace("M", ""));
    msg.payload = {
        action: "notify.mobile_app",
        data: {
            title: "Train delay",
            message: `Train to ${dest} is delayed ${delayMin} minutes.`
        }
    };
    return msg;
}
return null;
```

---

## Resrobot (national Sweden)

**What it provides:** Journey planner and real-time departures for all Swedish public transit
(SL, Skånetrafiken, Västtrafik, etc.) through one API.

**Auth:** API key in URL
**Base URL:** `https://api.resrobot.se/v2.1`
**Get key:** trafiklab.se → Register → Resrobot v2.1 API key (free)
**Rate limit:** 10,000 req/month (free)

### Find stop ID

```
GET https://api.resrobot.se/v2.1/location.name
  ?input=Gothenburg+Central
  &format=json
  &accessId=YOUR_KEY
```

### Get departures

```
GET https://api.resrobot.se/v2.1/departureBoard
  ?id=740000002
  &maxJourneys=10
  &format=json
  &accessId=YOUR_KEY
```

**Response:**
```json
{
  "Departure": [
    {
      "name": "Västtågen",
      "type": "REG",
      "stop": "Göteborg C",
      "time": "10:45:00",
      "date": "2026-03-14",
      "rtTime": "10:52:00",
      "direction": "Malmö C"
    }
  ]
}
```

### HA YAML REST sensor

```yaml
rest:
  - scan_interval: 120
    resource: "https://api.resrobot.se/v2.1/departureBoard?id=740000002&maxJourneys=5&format=json&accessId=YOUR_KEY"
    sensor:
      - name: "Next Departure Gothenburg"
        value_template: >-
          {% set deps = value_json.Departure %}
          {% if deps %}
            {% set d = deps[0] %}
            {{ d.name }} → {{ d.direction }}
            {% if d.rtTime is defined %}({{ d.rtTime }}){% else %}({{ d.time }}){% endif %}
          {% else %}No departures{% endif %}
```

---

## Entur (Norway)

**What it provides:** All Norwegian public transit - NSB/Vy trains, Ruter (Oslo),
Skyss (Bergen), Kolumbus (Stavanger). Journey planning and real-time departures.

**Auth:** None required for basic use (include `ET-Client-Name` header)
**Base URL:** `https://api.entur.io/journey-planner/v3/graphql`
**Rate limit:** Polite use, no official limit

### GraphQL query - next departures

```graphql
{
  stopPlace(id: "NSR:StopPlace:337") {
    name
    estimatedCalls(timeRange: 72100, numberOfDepartures: 5) {
      expectedDepartureTime
      destinationDisplay { frontText }
      serviceJourney {
        journeyPattern {
          line { id publicCode transportMode }
        }
      }
    }
  }
}
```

Common stop IDs:
- Oslo S: `NSR:StopPlace:337`
- Bergen: `NSR:StopPlace:548`
- Trondheim: `NSR:StopPlace:42108`

### Node-RED implementation

```javascript
// Function node - build Entur request
msg.payload = JSON.stringify({
    query: `{
        stopPlace(id: "NSR:StopPlace:337") {
            estimatedCalls(timeRange: 3600, numberOfDepartures: 3) {
                expectedDepartureTime
                destinationDisplay { frontText }
                serviceJourney {
                    journeyPattern {
                        line { publicCode transportMode }
                    }
                }
            }
        }
    }`
});
msg.headers = {
    "Content-Type": "application/json",
    "ET-Client-Name": "my-home-assistant"
};
return msg;
```

```json
{
  "type": "http request",
  "method": "POST",
  "url": "https://api.entur.io/journey-planner/v3/graphql",
  "ret": "obj"
}
```

```javascript
// Function node - extract next departures
const calls = msg.payload.data.stopPlace.estimatedCalls;
const departures = calls.map(c => {
    const t = new Date(c.expectedDepartureTime);
    const mins = Math.round((t - new Date()) / 60000);
    const line = c.serviceJourney.journeyPattern.line.publicCode;
    const dest = c.destinationDisplay.frontText;
    return `${line} → ${dest}: ${mins} min`;
});

msg.payload = {
    action: "input_text.set_value",
    target: { entity_id: "input_text.oslo_departures" },
    data: { value: departures.join(" | ") }
};
return msg;
```
