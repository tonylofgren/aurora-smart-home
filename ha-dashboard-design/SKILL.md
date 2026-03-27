---
name: HA Dashboard Design
description: >
  Beautiful, copy-paste-ready Home Assistant dashboard designs with complete CSS themes,
  card-mod styles, and button-card templates. Nine distinct visual styles: Glassmorphism,
  Dark Minimal, Material You, Nordic, Neon/Cyberpunk, Warm Home, Soft Pastel, Luxury Gold,
  and Retro Terminal. Use this skill whenever the user wants to make their dashboard look good,
  asks about card styling, CSS for Home Assistant, card-mod, button-card templates, Lovelace
  themes, dashboard aesthetics, or wants a specific visual style - even if they don't use the
  words "design" or "CSS".
source: https://github.com/tonylofgren/aurora-smart-home
---

# HA Dashboard Design

Copy-paste-ready dashboard designs for Home Assistant. Pick a style, copy the blocks you need.

## Prerequisites (install via HACS)

- **card-mod** - CSS styling for any card
- **button-card** - fully customizable button cards
- **mini-graph-card** - beautiful graphs (optional)
- **mushroom** - modern card suite (optional, used in some styles)

## Available Styles

| Style | Feel | Best for |
|-------|------|----------|
| `glassmorphism` | Frosted glass, depth, blur | Dark wallpaper backgrounds |
| `dark-minimal` | Pure black, clean typography | Focus, productivity |
| `material-you` | Google Material 3, dynamic color | Modern, familiar |
| `nordic` | Light, airy, Scandinavian | Bright rooms, day use |
| `neon-cyberpunk` | Glow effects, vivid neon | Night mode, wow factor |
| `warm-home` | Amber/orange, cozy | Living rooms, evening |
| `soft-pastel` | Soft pinks, lilac, mint | Friendly, family homes |
| `luxury-gold` | Deep navy + gold accents | Premium, sophisticated |
| `retro-terminal` | Green phosphor, monospace | Geek aesthetic |

## How to Use

1. Read the reference file for the chosen style
2. Copy the **Theme YAML** → paste into `config/themes/your-style.yaml`
3. Copy the **card-mod global styles** → paste into your dashboard resources
4. Copy individual **card blocks** → paste directly into your dashboard YAML
5. Adjust entity IDs to match your setup

## Quick Start - Any Style

```yaml
# configuration.yaml - enable themes folder
frontend:
  themes: !include_dir_merge_named themes/
```

```yaml
# Activate theme in dashboard
theme: your-theme-name
```

## Image Generation

To generate background images or dashboard mockup visualizations matching any style,
read `references/image-prompts.md` - contains ready-to-paste prompts for Midjourney,
DALL-E 3, Stable Diffusion, and Flux for every style.

## Reference Files

Read only the file for the requested style:

- `references/glassmorphism.md`
- `references/dark-minimal.md`
- `references/material-you.md`
- `references/nordic.md`
- `references/neon-cyberpunk.md`
- `references/warm-home.md`
- `references/soft-pastel.md`
- `references/luxury-gold.md`
- `references/retro-terminal.md`
- `references/image-prompts.md` - image generation prompts for backgrounds and mockups

## Card Types Covered in Every Style

Each reference file contains copy-paste blocks for:

- **Sensor display** - temperature, humidity, power readings
- **Media player** - Spotify, TV, speaker controls
- **Climate / thermostat** - temperature control with visual feedback
- **Security / alarm** - arm/disarm, door/window sensors
- **Camera** - live feed with overlay
- **Button grid** - scene/light/device shortcuts
- **Weather** - current + forecast display
- **Energy** - power consumption, solar, grid
- **Light control** - on/off, brightness, color temp slider
- **Presence** - person/device tracker cards
- **Calendar / agenda** - upcoming events
- **Statistics / graphs** - sensor history, mini-graph
- **Header / navigation** - page title, room nav
- **Alert banners** - notifications, warnings, status

## Dashboard Types

**Always default to `masonry`** - it works in all HA versions and requires no setup.

```yaml
# Safe default - works everywhere
views:
  - title: Home
    type: masonry   # ← default, always works
    cards:
      - ...
```

`type: sections` (HA 2024.6+ grid layout) can give a blank page if the user's HA version
doesn't support it or if the view structure is wrong. Only suggest it if the user explicitly
asks for it or confirms they're on HA 2024.6+.

## Pre-Output Checklist

- [ ] Dashboard uses `type: masonry` unless user specifically asked for Sections
- [ ] Theme YAML included with correct filename
- [ ] card-mod styles wrapped in correct YAML structure
- [ ] All entity IDs marked as placeholders (e.g., `sensor.YOUR_TEMPERATURE`)
- [ ] HACS dependencies listed at top of output
- [ ] Credentials/secrets not hardcoded

## Integration

**Pairs with:**
- `ha-yaml` skill - for automations that respond to dashboard interactions
- `api-catalog` skill - for sensor data displayed on the dashboard
