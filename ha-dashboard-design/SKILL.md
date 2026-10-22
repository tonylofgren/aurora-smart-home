---
name: HA Dashboard Design
description: >
  Bespoke Home Assistant dashboards with original layouts, typography, CSS themes,
  card-mod styles, and button-card templates. Nine distinct visual styles: Glassmorphism,
  Dark Minimal, Material You, Nordic, Neon/Cyberpunk, Warm Home, Soft Pastel, Luxury Gold,
  and Retro Terminal are starting points, not limits. Supports custom dashboards that do not
  look like the stock Home Assistant UI. Use when the user wants their own visual identity,
  asks about card styling, CSS for Home Assistant, card-mod, button-card templates, Lovelace
  themes, dashboard aesthetics, or wants a specific visual style - even if they don't use the
  words "design" or "CSS".
source: https://github.com/tonylofgren/aurora-smart-home
---

# HA Dashboard Design

Create a dashboard around the user's visual direction. Home Assistant supplies entities and
actions; its default card appearance is optional. The nine styles below are references,
not a menu the user must choose from.

## Choose the design approach

For an original theme, a reference screenshot, a wall panel, or a request that should not
look like Home Assistant, read [Custom dashboards](references/custom-dashboards.md).
Start with the intended screen, the information hierarchy, and the user's aesthetic.
Reuse supplied preferences; ask only for missing details that change the design.

- Theme only: preserve familiar cards and change colors, typography and surfaces.
- Custom composition: reshape the whole view with CSS Grid, button-card templates and
  original navigation. This is the usual choice for an app-like dashboard.
- Custom card or panel: use a maintained web component when the interaction cannot be
  expressed by existing cards. Do not force an independent frontend on a theme request.

Working starter: [Editorial dashboard](assets/custom-editorial/README.md), with separate
theme and dashboard files, responsive layouts and replaceable entity placeholders.

## Optional building blocks (install only those used)

- **card-mod** - CSS styling for supported cards, with shadow-DOM limits
- **button-card** - fully customizable button cards
- **mini-graph-card** - beautiful graphs (optional)
- **mushroom** - modern card suite (optional, used in some styles)
- **layout-card** - explicit responsive CSS Grid layouts (used by the editorial starter)

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

1. Read the requested style, or `references/custom-dashboards.md` for an original design
2. Copy the **Theme YAML** → paste into `config/themes/your-style.yaml`
3. Place card-level `card_mod: style:` under each target card. The old style references'
   "global styles" blocks are reusable card-level blocks, not dashboard resources.
   Resources register JavaScript modules; theme-wide card-mod uses its documented theme format.
4. Copy individual **card blocks** → paste directly into your dashboard YAML
5. Adjust entity IDs to match your setup

## Quick Start - Any Style

```yaml
# configuration.yaml - enable themes folder
frontend:
  themes: !include_dir_merge_named themes/
```

```yaml
# Activate a theme on a view, inside the dashboard's views list
views:
  - title: Home
    theme: your-theme-name
    type: sections
    sections: []
```

## Image Generation

To generate background images or dashboard mockup visualizations matching any style,
read `references/image-prompts.md` - contains ready-to-paste prompts for Midjourney,
DALL-E 3, Stable Diffusion, and Flux for every style.

## Reference Files

Read only the file for the requested style:

- `references/custom-dashboards.md` - original visual identities, layout choice, installation and QA
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

Choose for the layout, using the user's installed HA and custom-card versions:

| View | Use when |
|---|---|
| `sections` | Native responsive grouping and visual editing are useful; current HA default |
| `masonry` | Independently sized cards should flow into columns |
| `panel` | A full-width composition needs one root card, such as a layout-card grid |
| `custom:grid-layout` | Explicit CSS Grid placement and breakpoints are needed; requires layout-card |

Do not mix `sections:` and masonry `cards:` structures. A panel view has exactly one card.
An original appearance does not require hiding HA navigation. Offer kiosk behavior only when
requested, with an obvious route back to editing and without treating hidden controls as access control.

## Pre-Output Checklist

- [ ] Layout and visual identity match the request; no forced preset or masonry default
- [ ] Theme YAML included with correct filename
- [ ] card-mod styles wrapped in correct YAML structure
- [ ] All entity IDs marked as placeholders (e.g., `sensor.YOUR_TEMPERATURE`)
- [ ] HACS dependencies listed at top of output
- [ ] Credentials/secrets not hardcoded
- [ ] Dependencies, theme installation, resource registration and entity replacements documented
- [ ] Narrow/mobile and wide layouts considered; touch targets and visible text remain legible
- [ ] Missing/unavailable entities render honestly; critical actions retain confirmation
- [ ] Distinguish YAML/schema checks from actual live HA rendering and device interaction tests

For repository templates, placeholders are intentional and documented. For a user's live
dashboard, resolve real entity IDs (or explicitly identify unverified IDs). Write the dashboard,
theme and installation notes to disk; follow the Iris delivery contract in `aurora/souls/iris.md`.

## Integration

**Pairs with:**
- `ha-yaml` skill - for automations that respond to dashboard interactions
- `api-catalog` skill - for sensor data displayed on the dashboard
