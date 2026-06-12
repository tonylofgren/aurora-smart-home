# Home Assistant Reusable Jinja2 Macros Reference

**Source:** https://www.home-assistant.io/docs/configuration/templating/#reusing-templates

## Table of Contents
- [Core Concepts](#core-concepts)
- [File Layout](#file-layout)
- [Defining Macros](#defining-macros)
- [Importing Macros](#importing-macros)
- [Reloading](#reloading)
- [Limitations](#limitations)
- [Macro Recipes](#macro-recipes)
- [Troubleshooting](#troubleshooting)

---

## Core Concepts

If you paste the same template logic into five sensors, you have five places to fix when it breaks. Home Assistant lets you define Jinja2 macros once in `config/custom_templates/` and import them anywhere templates are rendered: template sensors, automations, scripts, dashboards, and the template editor.

A macro is a named, parameterized template block:

```jinja
{% macro greet(name) %}Hello {{ name }}!{% endmacro %}
```

Calling `greet('world')` renders the block with the argument substituted.

---

## File Layout

Create a `custom_templates` folder inside your configuration directory and put `.jinja` files in it:

```text
config/
├── configuration.yaml
└── custom_templates/
    ├── formatters.jinja
    ├── batteries.jinja
    └── climate.jinja
```

Rules:

- Only files ending in `.jinja` are loaded.
- Subfolders inside `custom_templates` are supported; import with the relative path (`'tools/text.jinja'`).
- One file can hold many macros. Group related macros per file so imports stay readable.

---

## Defining Macros

```jinja
{# formatters.jinja #}

{%- macro time_ago(dt) -%}
  {%- set seconds = (now() - dt) | abs | int(0, default=none) -%}
  {{- relative_time(dt) }} ago
{%- endmacro -%}

{%- macro pct(value, decimals=0) -%}
  {{- value | float(0) | round(decimals) }}%
{%- endmacro -%}
```

Macros support positional arguments, default values (`decimals=0`), and `varargs`. You can also share constants between templates with plain `{% set %}` at file level and import them by name.

---

## Importing Macros

Use `{% from %}` at the top of any template:

```yaml
template:
  - sensor:
      - name: "Washer finished ago"
        state: >
          {% from 'formatters.jinja' import time_ago %}
          {{ time_ago(states.sensor.washer_finished.last_changed) }}
```

Importing the whole file as a namespace also works:

```jinja2
{% import 'formatters.jinja' as fmt %}
{{ fmt.pct(states('sensor.cpu_load'), 1) }}
```

**Context matters.** By default an imported macro runs without the calling template's context. Home Assistant's own functions (`states()`, `now()`, `is_state()`, and friends) are globals and work either way, but if your macro reads variables from the calling template, import it `with context`:

```jinja2
{% from 'batteries.jinja' import battery_report with context %}
```

When unsure, `with context` is the safe default.

---

## Reloading

Edited `.jinja` files are not picked up automatically. Reload them with either:

- UI: Developer tools > YAML > "Custom Jinja2 templates" under the reload section.
- Action call:

```yaml
actions:
  - action: homeassistant.reload_custom_templates
```

No restart is needed. Template entities re-render with the new macro on their next update; force one with `homeassistant.update_entity` if you want to verify immediately.

---

## Limitations

- **Macros return strings.** Whatever the macro renders comes back as text. `{{ my_macro() == 5 }}` is false even if the macro prints `5`; cast at the call site: `{{ my_macro() | int }}`. Returning lists or dicts requires serializing (`| to_json` inside the macro, `| from_json` outside).
- **Whitespace leaks into the result.** Every newline and indent inside the macro body becomes part of the returned string. Use `{%-` and `-%}` to strip whitespace around tags, and trim at the call site (`{{ my_macro() | trim }}`) when needed.
- **No state of their own.** Macros cannot persist values between calls. Use helpers or trigger-based template sensors for memory.
- **Imports are per template.** Each template that uses a macro needs its own `{% from %}` line; there is no global auto-import.

---

## Macro Recipes

### Friendly time-ago formatter

`relative_time()` gives "5 minutes"; this wraps it into a sentence and handles fresh timestamps.

```jinja
{# formatters.jinja #}
{%- macro time_ago(dt) -%}
  {%- if dt is none -%}
    never
  {%- elif (now() - dt).total_seconds() < 60 -%}
    just now
  {%- else -%}
    {{ relative_time(dt) }} ago
  {%- endif -%}
{%- endmacro -%}
```

```jinja2
# Anywhere a template renders:
{% from 'formatters.jinja' import time_ago %}
Front door last opened {{ time_ago(states.binary_sensor.front_door.last_changed) }}.
```

### Battery level report

Iterates all battery sensors below a threshold and renders one line each. Useful in notifications and markdown cards.

```jinja
{# batteries.jinja #}
{%- macro battery_report(threshold=25) -%}
  {%- set low = states.sensor
      | selectattr('attributes.device_class', 'defined')
      | selectattr('attributes.device_class', 'eq', 'battery')
      | selectattr('state', 'is_number')
      | selectattr('state', 'lt', threshold | string)
      | sort(attribute='state') -%}
  {%- if low | list | count == 0 -%}
    All batteries above {{ threshold }}%.
  {%- else -%}
    {%- for s in low %}
{{ s.name }}: {{ s.state }}%
    {%- endfor -%}
  {%- endif -%}
{%- endmacro -%}
```

```yaml
actions:
  - action: notify.mobile_app_phone
    data:
      title: "Low batteries"
      message: >
        {% from 'batteries.jinja' import battery_report %}
        {{ battery_report(20) }}
```

### Temperature trend arrow

Compares a sensor against a statistics sensor (or any baseline entity) and returns a direction symbol.

```jinja
{# climate.jinja #}
{%- macro trend(current_entity, baseline_entity, deadband=0.3) -%}
  {%- set cur = states(current_entity) | float(none) -%}
  {%- set base = states(baseline_entity) | float(none) -%}
  {%- if cur is none or base is none -%}
    ?
  {%- elif cur - base > deadband -%}
    rising
  {%- elif base - cur > deadband -%}
    falling
  {%- else -%}
    steady
  {%- endif -%}
{%- endmacro -%}
```

```yaml
template:
  - sensor:
      - name: "Outdoor temperature trend"
        state: >
          {% from 'climate.jinja' import trend %}
          {{ trend('sensor.outdoor_temp', 'sensor.outdoor_temp_mean_1h') }}
```

Pair it with a statistics sensor (`platform: statistics`, `state_characteristic: mean`) as the baseline.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `TemplateNotFound: file.jinja` | Wrong filename, wrong extension, or file outside `custom_templates/` | Check the path; only `.jinja` files load |
| Edits have no effect | Templates not reloaded | Run `homeassistant.reload_custom_templates` |
| Macro renders with stray spaces or newlines | Whitespace inside macro body | Add `{%-`/`-%}` trims, or `| trim` at the call site |
| Comparison against macro output fails | Macros return strings | Cast: `{{ my_macro() | int }}` |
| `'x' is undefined` inside the macro | Macro uses caller variables without context | Import `with context` |

Test macros interactively in Developer tools > Template: paste the `{% from %}` line plus a call and iterate there before touching your sensors.
