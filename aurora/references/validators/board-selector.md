# Board Selector

Helps Volt recommend the right board for a project, or tell users what a board they already own is good for. Runs BEFORE pin allocation (which board) and BEFORE pin-validator (validate the chosen board).

## When to Run

Volt runs this when:
- User describes a project but has not selected a board yet
- User asks "what board should I use for X?"
- User says "I have a [board], what can I build?"

## Inputs

- `requirements`: object describing user needs, e.g.:
  ```
  {
    "needs_bluetooth_proxy": true,
    "needs_battery_power": true,
    "needs_voice_assistant": false,
    "needs_matter": true,
    "needs_thread": false,
    "needs_zigbee": false,
    "max_gpio_needed": 6,
    "form_factor_preference": "compact"
  }
  ```
- `owned_board_id`: optional, set if user already has a specific board

## Logic

### Mode A: Recommend a board

1. Load all profiles from `aurora/references/boards/**/*.json`
2. Filter by required capabilities:
   - If `needs_bluetooth_proxy` is true, keep boards where `smart_home_capabilities.bluetooth_proxy` is true
   - Same for `voice_assistant`, `matter_controller`, `zigbee_coordinator`, `thread_border_router`, `ble_tracker`
3. Filter out boards where `lifecycle.status` is `deprecated` or `obsolete` (warn but allow `legacy`)
4. Prefer boards where `recommended_for` mentions the user's primary use case
5. Avoid boards where `not_recommended_for` mentions the user's constraints
6. Rank by `lifecycle.status` (active > legacy > experimental) and `last_verified` recency
7. Present top 2-3 with trade-offs from `recommended_for` / `not_recommended_for`

### Mode B: User already owns a board

1. Load that profile by `board_id`
2. List use cases from `recommended_for`
3. List warnings from `not_recommended_for` and any `lifecycle` reason
4. If the user's stated goal appears in `not_recommended_for`, flag it explicitly and suggest a more suitable board (using `lifecycle.successor` if `legacy`)

## Output

```
{
  "primary": "<board_id>",
  "alternatives": ["<board_id>", "<board_id>"],
  "warnings": ["..."],
  "rationale": "<plain language explanation>"
}
```

## Example

Input:
```
{"needs_bluetooth_proxy": true, "needs_matter": true, "needs_battery_power": true}
```

Output:
```
{
  "primary": "esp32-c6-devkit",
  "alternatives": ["esp32-s3-devkitc-1", "esp32-c3-mini"],
  "warnings": [],
  "rationale": "ESP32-C6 is the best fit: BLE 5.0 for proxy, Matter native, Thread/Zigbee for future expansion, deep sleep 7uA. ESP32-S3 also works but is overkill for power and price. ESP32-C3 is cheapest and works for proxy+Matter but lacks Thread."
}
```

Input (Mode B):
```
{"owned_board_id": "d1-mini", "goal": "bluetooth proxy"}
```

Output:
```
{
  "primary": "d1-mini",
  "warnings": [
    "D1 Mini has no Bluetooth radio. Cannot build bluetooth proxy.",
    "Board is legacy; ESP32-C3 Super Mini is the recommended successor."
  ],
  "rationale": "D1 Mini cannot do bluetooth proxy. Use it for WiFi-only projects (simple sensors, IR blaster, relay bridges). For bluetooth proxy, buy an ESP32-C3 Super Mini (same form factor)."
}
```

## Volt Integration

Volt's Iron Law 6 covers this: load the relevant profile, run the validator, refuse to proceed if board does not match requirements. Board selector adds the up-front "which board?" step before pin-validator and conflict-validator can run.
