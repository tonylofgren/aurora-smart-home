---
name: notification-hub
intent: Get useful, actionable phone notifications without the spam
specialists: [Sage]
hardware: false
match_keywords: [notification, alert, notify, mobile, push, actionable, reminder, doors, laundry, battery, quiet hours]
related_example: examples/mailbox-notifier
---

# Notification Hub

## What you get

A reusable notification pattern so your alerts are useful instead of noise: actionable buttons (dismiss, snooze, act), quiet hours, and a single place to tune them. Build it once and every automation routes through it. No new hardware: it uses the HA companion app you already have.

## Automation pattern

1. **Reusable script:** a `notify` script that takes title, message, target, priority, and optional action buttons. Every other automation calls this script instead of `notify.mobile_app_*` directly.
2. **Quiet hours:** the script checks an `input_datetime`/`input_boolean` and downgrades non-critical messages to silent at night.
3. **Actionable handling:** an automation listens for `mobile_app_notification_action` events and runs the matching action (e.g. "Mark laundry done", "Open garage anyway").
4. **Example callers:** door left open 10 min, washing machine cycle ended, a device battery below 15%.

Modern syntax: callers use `action: script.notify_hub` with `data:` for the parameters.

## Dashboard skeleton

- A "notifications" view listing recent alerts (from a logbook or `input_text` log).
- Toggles for quiet hours and per-category mute booleans.
- Test button that fires a sample notification.

## Customise

- **Quiet hours:** start/end times and which priorities ignore them.
- **Categories:** security, appliances, batteries, info; each with its own mute.
- **Action buttons:** which actions appear per notification type.
- **Targets:** which phones/people receive which categories.

## Build it

Pick this and Sage generates the reusable notify script, the action-handler automation, the quiet-hours helpers, and a few example callers. No device to build. Read `examples/mailbox-notifier` for an actionable-notification automation end to end.
