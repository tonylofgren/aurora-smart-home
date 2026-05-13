# Async Correctness Validator

Flags synchronous calls inside Home Assistant Python integration code. Home Assistant's event loop is single-threaded; one blocking call (`time.sleep`, `requests.get`, naive datetime arithmetic, sync file I/O) freezes every entity update, every automation, every dashboard for the duration of the call. The classic failure mode is "automation is slow during business hours" because someone's REST integration uses `requests` instead of `aiohttp`.

This validator targets a fixed list of high-risk patterns. It does NOT attempt to statically prove async-correctness of arbitrary code — that requires a real Python AST analysis. The goal here is to catch the common, well-known mistakes before they ship.

## When to Run

Ada MUST run this validator before delivering any Python code that targets `custom_components/` or the broader HA core integration. The validator runs on the generated source as a whole, before the user sees it.

Mira (LLM/AI integration agent) runs it too when producing Python conversation-agent code.

## Inputs

- `python_text`: the full Python source about to be delivered, as a UTF-8 string.
- `file_path`: optional path the file will be written to. Used only for error messages.

## Forbidden Patterns

The validator flags these exact call patterns. Each pattern lists the recommended async replacement so failure messages are actionable.

| Pattern | Replacement | Why |
|---------|-------------|-----|
| `datetime.now()` | `dt_util.now()` | HA's `dt_util` handles timezones; naive datetimes corrupt state attributes |
| `datetime.utcnow()` | `dt_util.utcnow()` | Same reason; HA enforces tz-aware UTC |
| `time.sleep(` | `await asyncio.sleep(` | Blocks the event loop for the full duration |
| `requests.get(` | `aiohttp.ClientSession` | `requests` is blocking; use the existing aiohttp_client helper |
| `requests.post(` | `aiohttp.ClientSession` | Same |
| `requests.put(` | `aiohttp.ClientSession` | Same |
| `requests.delete(` | `aiohttp.ClientSession` | Same |
| `urllib.request.urlopen(` | `aiohttp.ClientSession` | Sync HTTP |
| `urllib.request.Request(` | `aiohttp.ClientSession` | Sync HTTP |
| `subprocess.run(` | `asyncio.create_subprocess_exec` | Spawns and waits synchronously |
| `subprocess.call(` | `asyncio.create_subprocess_exec` | Same |
| `subprocess.check_output(` | `asyncio.create_subprocess_exec` | Same |
| `open(` outside `hass.async_add_executor_job` | `await hass.async_add_executor_job(open, ...)` | Sync file I/O blocks the loop |

The `open(` rule is the trickiest — `open` is fine in `__init__` and module-scope, only inside async functions or coroutines is it a problem. The validator emits a warning rather than a failure when `open(` is detected, and includes the line number so Ada can manually verify the context.

## Checks

For each forbidden pattern in the list above:

1. **Line-by-line scan** — find every occurrence of the pattern's literal text in `python_text`. Each hit produces a failure (or warning, for `open(`):
   - `'<file_path>' line <N>: '<pattern>' is forbidden in async HA code. Replace with '<replacement>'. <Why row from table>.`

2. **Import-line exemption** — if the line begins with `import ` or `from `, do NOT flag the pattern. `import requests` for example is legal; only the call sites matter.

3. **Comment exemption** — if the pattern occurs inside a `# ...` comment or a `"""..."""` docstring, do NOT flag it.

4. **dt_util.now() lookalike** — `dt_util.now()` itself is the recommended replacement, so do NOT flag the substring `dt_util.now()` even though it contains `now()`.

5. **String literal exemption** — if the pattern occurs inside a string literal (quoted with `"`, `'`, `"""`, `'''`), do NOT flag it. Catching `"datetime.now()"` in a log message string is a false positive.

## Output

- Pass: empty failures list.
- Warnings: list of warning strings. Ada surfaces these but does not block delivery.
- Failures: list of failure strings. Ada MUST NOT deliver the file if non-empty.

## Why This List Is Narrow

The validator does not attempt to detect:

- All sync calls in async functions (requires AST + type info)
- Blocking dependencies (e.g. a library that calls `requests` internally)
- Long CPU-bound loops in coroutines

Those need real static analysis. The current list is the eighty-percent of real-world bugs that appear when an LLM-generated HA integration ships without review. Extending the list is a deliberate decision — add to the table above, never invent a generic "looks blocking" heuristic.

## Examples

### Example 1: Naive datetime

Input (`custom_components/myintegration/sensor.py`):
```python
from datetime import datetime

async def async_update(self):
    self._attr_state = datetime.now().isoformat()
```

Output:
```
Failures:
- 'custom_components/myintegration/sensor.py' line 4: 'datetime.now()' is forbidden in async HA code. Replace with 'dt_util.now()'. HA's dt_util handles timezones; naive datetimes corrupt state attributes.
```

### Example 2: requests.get

Input (`custom_components/myintegration/api.py`):
```python
import requests

class CloudClient:
    def fetch(self, url):
        return requests.get(url, timeout=10).json()
```

Output:
```
Failures:
- 'custom_components/myintegration/api.py' line 5: 'requests.get(' is forbidden in async HA code. Replace with 'aiohttp.ClientSession'. requests is blocking; use the existing aiohttp_client helper.
```

Ada's fix:

```python
from homeassistant.helpers.aiohttp_client import async_get_clientsession

class CloudClient:
    def __init__(self, hass):
        self._session = async_get_clientsession(hass)

    async def fetch(self, url):
        async with self._session.get(url, timeout=10) as resp:
            return await resp.json()
```

### Example 3: time.sleep in coroutine

Input:
```python
async def async_setup(hass, config):
    await some_setup()
    time.sleep(2)
    return True
```

Output:
```
Failures:
- 'config.py' line 3: 'time.sleep(' is forbidden in async HA code. Replace with 'await asyncio.sleep('. Blocks the event loop for the full duration.
```

### Example 4: open() warning

Input:
```python
async def _read_config(self):
    with open('/etc/myintegration.conf') as f:
        return f.read()
```

Output:
```
Warnings:
- 'service.py' line 2: 'open(' detected inside what looks like an async function. Sync file I/O blocks the event loop. Verify the context and wrap with `await hass.async_add_executor_job(open, ...)` if this is in an event-loop call.
Failures: []
```

The validator warns but does not block — Ada manually confirms whether the `open()` is in an async context.

### Example 5: Healthy code

Input:
```python
from homeassistant.util import dt as dt_util

async def async_update(self):
    self._attr_state = dt_util.now().isoformat()
```

Output:
```
Failures: []
Warnings: []
```

`dt_util.now()` is the recommended replacement and is intentionally not flagged.

### Example 6: Forbidden pattern in a docstring (exempt)

Input:
```python
async def async_update(self):
    """Update the sensor. Do not use datetime.now() here."""
    self._attr_state = dt_util.now().isoformat()
```

Output:
```
Failures: []
Warnings: []
```

The reference inside the docstring is documentation, not a call.
