# Recipe Format

A recipe is a curated starting point, not a finished project. It is lighter than a worked example in `examples/`: it names the hardware, sketches the automation and dashboard, and lists the few parameters the user actually changes. Aurora reads a recipe and generates a full project folder from it (the recipe-to-project flow in `aurora/SKILL.md`), then the user customises.

Recipes exist to lower onboarding friction from "figure out everything" to "pick and customise". They are the smaller, opinionated subset; the 27 projects in `examples/` are the comprehensive reference gallery.

## File location

One file per recipe at `aurora/recipes/<slug>.md`. The slug is lowercase-kebab and matches the `name` in the header. Every recipe is listed in `aurora/recipes/_index.md`.

## Required header

Each recipe opens with a fenced metadata block so Aurora can match intent without reading the whole file:

```
---
name: co2-monitor
intent: Track indoor CO2 and get alerted when air gets stuffy
specialists: [Volt, Sage]
hardware: true
match_keywords: [co2, carbon dioxide, air quality, stuffy, ventilation, scd40]
related_example: examples/air-quality-multi
---
```

- `hardware: false` recipes are pure Home Assistant (no device to build); they skip the Hardware and Wiring sections.
- `specialists` names which souls the recipe-to-project flow will load.
- `match_keywords` drives the "suggest 3-5 recipes" step in the opening question.
- `related_example` links the full worked project when one exists, else omit the key.

## Required sections

1. **What you get** - one short paragraph: the outcome, not the parts list.
2. **Hardware** (skip when `hardware: false`) - a BOM skeleton table: Part, Purpose, LCSC, Notes. LCSC numbers come from `aurora/references/components/` and are never invented; use `TBD` when the part is not in the catalog.
3. **Wiring** (skip when `hardware: false`) - the few connections that matter, as a short list or ASCII sketch. The generated project gets the full WIRING.md.
4. **Automation pattern** - the core logic as a numbered sketch (trigger, condition, action), not full YAML. Modern HA syntax in any snippet (`triggers:`, `actions:`, `action:`).
5. **Dashboard skeleton** - the cards that make the feature usable, named, not fully styled.
6. **Customise** - the 3-6 parameters the user changes (thresholds, entity names, rooms, schedules). This is the point of a recipe.
7. **Build it** - one line stating what Aurora produces when the user picks this recipe, and which example to read for the complete version.

## Rules

- English only (the repo is public and global), no em or en dashes (see the no-em-dash feedback rule).
- Hardware recipes cite verified components; never guess an LCSC number or a price.
- Keep a recipe under ~120 lines. If it needs more, it is an example, not a recipe.
- A recipe that maps onto an existing `examples/` project links it in `related_example` so the user can read the finished version.
- Recipes are starting points: prefer the common, safe default and name the alternatives in Customise rather than branching the whole recipe.
