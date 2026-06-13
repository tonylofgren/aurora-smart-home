---
name: energy-dashboard
intent: See where your electricity goes and what it costs, at a glance
specialists: [Iris, Sage]
hardware: false
match_keywords: [energy, power, electricity, consumption, cost, kwh, monitoring, dashboard, usage, bill]
related_example: examples/energy-monitor
---

# Energy Dashboard

## What you get

A clear view of household power: what is drawing now, today versus yesterday, the top consumers, and an estimated cost from your current tariff. Built from power/energy entities you already have (smart plugs, a CT clamp, an inverter, or the native HA Energy integration), so no new hardware is required.

## Automation pattern

This recipe is mostly visualisation plus a few helper sensors, not heavy automation:

1. **Cost sensor:** a template sensor multiplying live power by the current price (static, or from a Tibber/Nordpool entity via the api-catalog skill).
2. **Daily total:** a `utility_meter` resetting at midnight for kWh/day and cost/day.
3. **Optional alert:** notify when instantaneous power exceeds a ceiling (something heavy left on), or when daily cost passes a budget line.

## Dashboard skeleton

- Big number: current total power (W).
- Today vs yesterday bar comparison (kWh and cost).
- Top-consumers list sorted by power.
- ApexCharts or history-graph for the last 24h.
- Tariff chip showing the current price when a dynamic-price entity exists.

## Customise

- **Tariff:** flat rate as a default `input_number`, or wire a dynamic-price sensor.
- **Currency and units:** match your locale.
- **Power ceiling:** threshold for the "something heavy is on" alert.
- **Sources:** which power/energy entities feed the totals.

## Build it

Pick this and Sage generates the cost template sensor and utility meters while Iris lays out the dashboard. No device to build. Read `examples/energy-monitor` for the version wired to a CT-clamp power sensor, and use the api-catalog skill to add Tibber or Nordpool dynamic pricing.
