# Packages & Modular Configuration

Reuse YAML across many devices with the `packages:` component. One shared file per concern (wifi, diagnostics, base hardware), and each device file shrinks to the few lines that actually differ.

**Source:** https://esphome.io/components/packages/

## Table of Contents
- [Why Packages](#why-packages)
- [Local Packages](#local-packages)
- [Passing Variables with vars](#passing-variables-with-vars)
- [Remote Packages (git)](#remote-packages-git)
- [How Substitutions Interact with Packages](#how-substitutions-interact-with-packages)
- [Modifying Packaged Config: !extend and !remove](#modifying-packaged-config-extend-and-remove)
- [Fleet Pattern: 20-Line Device Files](#fleet-pattern-20-line-device-files)
- [Merge Rules and Gotchas](#merge-rules-and-gotchas)

---

## Why Packages

Without packages, ten sensor nodes means ten copies of the same wifi, api, ota, and logger blocks. Every change (new OTA password scheme, new diagnostic sensor) must be edited ten times. With packages, shared config lives in one file and every device pulls it in with a single line.

Rule of thumb: as soon as a second device repeats a block, move that block into a package.

## Local Packages

Each entry under `packages:` is a name mapped to an `!include`:

```yaml
packages:
  wifi: !include common/wifi.yaml
  diagnostics: !include common/diagnostics.yaml
```

The included files are plain ESPHome YAML fragments:

```yaml
# common/wifi.yaml
wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password
  ap:
    ssid: "${name} Fallback"
    password: !secret fallback_password

captive_portal:
```

Package contents are merged into the device config. Anything the device file defines itself wins over what a package provides (see [Merge Rules](#merge-rules-and-gotchas)).

## Passing Variables with vars

The map form of `!include` accepts a `vars:` block, so one package file can serve devices with different values. Inside the package, reference the variables with `${...}` like substitutions:

```yaml
# Device file
packages:
  temperature_board: !include
    file: common/dallas-temp.yaml
    vars:
      sensor_name: "Garage Temperature"
      poll_interval: 60s
```

```yaml
# common/dallas-temp.yaml
sensor:
  - platform: dallas_temp
    name: ${sensor_name}
    update_interval: ${poll_interval}
```

The same package can be included more than once under different package names with different `vars`, which is how you stamp out repeated hardware (four identical relay channels, for example).

## Remote Packages (git)

Packages can be pulled from a git repository, which is how community base configs and company-wide fleet repos are shared:

```yaml
packages:
  remote_base:
    url: https://github.com/your-org/esphome-fleet
    ref: main          # branch, tag, or commit
    files: [base.yaml, wifi.yaml]
    refresh: 1d        # how often to re-fetch; default 1d
```

Notes:

- `files:` lists which YAML files inside the repo to merge. Entries can also be maps with `path:` and `vars:` to pass variables per file.
- `refresh:` controls cache age. Use `0s` to force a fresh pull on every compile, or a long interval for stability. Pin `ref:` to a tag or commit for reproducible fleet builds.
- A shorthand URL form also works for single files:

```yaml
packages:
  - github://your-org/esphome-fleet/base.yaml@main
```

Since 2026.6.0 the short form (and `dashboard_import`) also accepts Codeberg alongside GitHub and GitLab, using `codeberg://owner/repo/path/file.yaml`. PR #16501.

```yaml
packages:
  - codeberg://your-org/esphome-fleet/base.yaml@main
```

Treat remote packages like any dependency: pin the version, review changes before bumping, and prefer your own fork over a stranger's repo for anything flashed to real hardware.

## How Substitutions Interact with Packages

Packages may define `substitutions:` as defaults, and the device file may override them. Substitutions in the device YAML take precedence over substitutions from a package, so the pattern is:

```yaml
# common/base.yaml - safe defaults
substitutions:
  log_level: INFO
  update_interval: 60s
```

```yaml
# device file - overrides only what differs
substitutions:
  name: greenhouse-node
  friendly_name: Greenhouse Node
  update_interval: 30s   # overrides the package default
packages:
  base: !include common/base.yaml
```

Use `substitutions` for values that many components in many files share (device name, room). Use `vars:` for values that belong to one specific include, especially when the same package file is included several times.

## Modifying Packaged Config: !extend and !remove

When a package gets 90% of the way there, you do not need to fork it. Two directives adjust merged config from the device file:

`!extend` targets an `id:` defined in a package and merges extra options into that component:

```yaml
# Package defines: sensor: - platform: uptime, id: uptime_sensor
sensor:
  - id: !extend uptime_sensor
    update_interval: 120s
```

`!remove` deletes something a package added. It works on a component by id, or on a whole top-level key:

```yaml
sensor:
  - id: !remove uptime_sensor   # drop one packaged sensor

captive_portal: !remove          # drop an entire packaged block
```

This keeps the package file generic and pushes per-device exceptions to the device file, where they are visible.

## Fleet Pattern: 20-Line Device Files

A practical layout for a fleet of similar nodes:

```
fleet/
  common/
    base.yaml      # esphome name/min_version, logger, api, ota
    wifi.yaml      # wifi + fallback AP + captive_portal
    sensors.yaml   # uptime, wifi_signal, restart button
  garage-node.yaml
  greenhouse-node.yaml
```

```yaml
# common/base.yaml
esphome:
  name: ${name}
  friendly_name: ${friendly_name}
  min_version: 2025.5.0

logger:
api:
  encryption:
    key: !secret api_encryption_key
ota:
  - platform: esphome
    password: !secret ota_password
```

Each device file then carries only identity, packages, and its unique hardware:

```yaml
# greenhouse-node.yaml
substitutions:
  name: greenhouse-node
  friendly_name: Greenhouse Node

esp32:
  board: esp32dev

packages:
  base: !include common/base.yaml
  wifi: !include common/wifi.yaml
  diagnostics: !include common/sensors.yaml

sensor:
  - platform: dht
    pin: GPIO4
    temperature:
      name: "Greenhouse Temperature"
    humidity:
      name: "Greenhouse Humidity"
```

Adding device eleven to the fleet is a 20-line file, and a fleet-wide change (say, SHA256 OTA auth) is one edit in `common/base.yaml`.

## 2026.6.0 Additions

### YAML Frontmatter Metadata

A leading `---`-delimited YAML block at the top of a file is now treated as opaque per-file metadata. It is stripped before validation, so it never reaches the config schema, and it is captured on `CORE.frontmatter` for tooling to read (author, version, labels, and similar). PR #16552. This lets fleet tooling tag files without ESPHome rejecting unknown keys.

```yaml
author: Jane Doe
version: 1.0.0
labels: [office, climate]
---
esphome:
  name: my-node
```

### Top-Level esphome.build_flags

`esphome.build_flags` now applies compiler flags on both native ESP-IDF and PlatformIO builds. The older `platformio_options.build_flags` was PlatformIO-only, so build flags previously dropped silently under the native ESP-IDF path. PR #16629.

```yaml
esphome:
  name: my-node
  build_flags:
    - "-DMY_DEFINE=1"
```

Prefer `esphome.build_flags` for portable defines so a later framework switch does not quietly lose them.

## Merge Rules and Gotchas

- **Device file wins.** Keys set directly in the device YAML override the same keys coming from a package.
- **Dictionaries merge, component lists append.** A `sensor:` list in a package and one in the device file are combined; use `!extend` / `!remove` with ids to change packaged entries instead of duplicating them.
- **Avoid the same key in two packages.** Cross-package precedence is easy to get wrong; keep each concern (wifi, ota, diagnostics) in exactly one package file.
- **Give packaged components ids.** Without an `id:` there is nothing for `!extend` or `!remove` to target later.
- **Remote refresh can surprise you.** A `ref: main` package with default `refresh:` silently picks up upstream changes on the next compile after the cache expires. Pin tags for production fleets.

Full 2026.6.0 details: references/release-2026-6.md
