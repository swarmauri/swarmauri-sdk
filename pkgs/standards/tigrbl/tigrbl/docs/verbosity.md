# Tigrbl verbosity and uvicorn logging

Tigrbl logs through the `uvicorn` logger. This keeps its output aligned with the
server's log configuration, so debug statements only appear when uvicorn is
started in verbose mode.

## Default behavior

By default, uvicorn runs at `INFO` level and suppresses debug output. Tigrbl does
not override that setting, so debug messages stay hidden unless you opt in.

## Enabling verbose output

Use uvicorn's log-level to opt into debug output:

```bash
uvicorn your_module:app --log-level debug
```

Or configure it programmatically:

```python
import uvicorn

config = uvicorn.Config("your_module:app", log_level="debug")
server = uvicorn.Server(config)
```

## Disabling verbose output

Set the log level back to `info` (or higher) to suppress debug messages:

```bash
uvicorn your_module:app --log-level info
```
