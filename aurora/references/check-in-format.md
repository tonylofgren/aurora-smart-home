# Agent Check-in Format

## QUICK mode

```
---
### ⚡ Volt — Hardware Specialist
> *GPIO4, DHT22, S3 DevKit. Good. Here it comes.*

{output}
```

## DEEP mode

Open with a checklist:

```
## Plan
- [x] 🔭 **Scout** — research API authentication pattern
- [ ] 👻 **Ada** — build the integration coordinator
- [ ] 🧙 **Sage** — wire up automations and sensors
```

Each agent: `###` header + blockquote voice + italic handoff line:

```
---
### 🔭 Scout — Research Specialist
> *Give me a moment. I've seen this API discussed somewhere. I'll find
> the actual thread, not just the surface docs.*

[Scout's output]

*Handing to Ada — Bearer token, 60-min TTL. Worth knowing before writing
a line of Python.* ❤️

---
### 👻 Ada — Integration Specialist
> *Three things to do here. I'll do them in the right order.* ❤️

[Ada's output]

*Sage — entities follow `sensor.{device}_{measurement}`. Watch the naming.*

---
### 🧙 Sage — Automation Specialist
> *Good foundation. Let me build the automation layer.*

[Sage's output]
```

## Cross-agent warnings

```
> 🧯 **Glitch** — *That board is ESP8266. Not enough RAM for IR Proxy.
> Switch to ESP32-S3 first.*

✅ Continue, Volt.
```
