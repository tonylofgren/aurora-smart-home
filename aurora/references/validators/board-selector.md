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

1. Load all profiles from `aurora/references/boards/**/*.json` — profiles are spread across subdirectories: `esp32/`, `esp8266/`, `rp/`, `special/`, `smart-home/`. Search MUST be recursive (`**`); a flat search misses `special/` and `smart-home/` entirely.
2. Filter by required capabilities:
   - If `needs_bluetooth_proxy` is true, keep boards where `smart_home_capabilities.bluetooth_proxy` is true
   - Same for `voice_assistant`, `matter_controller`, `zigbee_coordinator`, `thread_border_router`, `ble_tracker`
3. Filter out boards where `lifecycle.status` is `deprecated` or `obsolete` (warn but allow `legacy`)
4. Filter out boards where `board_type` is `commercial_device` — these are flash-only targets, not fresh builds
5. Prefer boards where `recommended_for` mentions the user's primary use case
6. Avoid boards where `not_recommended_for` mentions the user's constraints
7. Rank by `lifecycle.status` (active > legacy > experimental) and `last_verified` recency
8. Present top 2-3 with trade-offs from `recommended_for` / `not_recommended_for`

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

### Mode C: User is designing a custom PCB (bare chip/module)

Triggered when the user says "custom board", "custom PCB", "bare chip", "bare module", "designing my own board", or "production hardware".

1. Load all profiles from `aurora/references/boards/module/**/*.json`
2. Filter by required capabilities (same logic as Mode A)
3. Present top 1-2 modules with:
   - Chip capabilities relevant to the project
   - `esphome.board` value to use in YAML (nearest dev kit ID, since ESPHome has no bare-module board IDs)
   - Key `limitations.strapping_conflict_warnings` (especially: no onboard regulator, no USB-UART)
4. Always add this guidance block after the recommendation:

```
Custom PCB workflow:
1. Prototype with the corresponding dev kit first (esphome.board value above)
2. Validate your GPIO assignments on the dev kit before committing to PCB layout
3. When your ESPHome config is working, swap the carrier board for this module — the board: ID stays the same
4. Add a 3.3V LDO (e.g. AMS1117-3.3) and a USB-UART bridge (e.g. CP2102) or expose GPIO19/20 for native USB flashing
```

## Volt Integration

Volt's Iron Law 6 covers this: load the relevant profile, run the validator, refuse to proceed if board does not match requirements. Board selector adds the up-front "which board?" step before pin-validator and conflict-validator can run.
