# Peagen Deployment Guide

This document explains how to launch the Peagen gateway and worker services and how to submit tasks.

## Requirements

* Python 3.10+
* Redis server – used for queues and WebSocket events
* PostgreSQL database – used by the gateway for the results backend
* `peagen` package installed (editable mode is fine)
* `uvicorn` available on the PATH
* Docker (optional) for containerized deployments

Environment variables control the runtime configuration. A minimal `.peagen.toml` is required in the working directory for both services.

For quick local testing you can rely on the in-memory queue and filesystem result backend:

```toml
[queues]
default_queue = "in_memory"

[result_backends]
default_backend = "local_fs"
[result_backends.adapters.local_fs]
root_dir = "./task_runs"
```

Production deployments typically use Redis and Postgres instead:

```toml
[queues]
# Use Redis for production; in-memory queue only for testing
default_queue = "redis"
[queues.adapters.redis]
uri = "${REDIS_URL}"

[result_backends]
# Store task results in Postgres
default_backend = "postgres"
[result_backends.adapters.postgres]
dsn = "${PG_DSN}"
```

## Running the Gateway

1. Ensure Redis and PostgreSQL are reachable and the environment variables below are set:
   * `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_PASSWORD`
   * `PG_HOST`, `PG_PORT`, `PG_DB`, `PG_USER`, `PG_PASS`
2. Place a `.peagen.toml` in the current directory (see example above).
3. Start the gateway with Uvicorn:

```bash
uvicorn peagen.gateway:app --host 0.0.0.0 --port 8000
```

The gateway exposes a JSON‑RPC endpoint at `/rpc` and a WebSocket at `/ws/tasks`.
You can also build a Docker image and run it:

```bash
# Dockerfile should install peagen and copy your .peagen.toml
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install peagen
CMD ["uvicorn", "peagen.gateway:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Running a Worker

Workers connect to the gateway via JSON‑RPC and advertise task handlers. Set these variables before launching:

* `DQ_GATEWAY` – URL of the gateway RPC endpoint (e.g. `http://localhost:8000/rpc`)
* `DQ_POOL` – name of the worker pool (defaults to `default`)
* `DQ_HOST` – IP address the worker should advertise (set to `127.0.0.1` if no network)
* `PORT` – port the worker will listen on (default `8001`)
* `DQ_FAIL_MAX` – number of consecutive failures before opening the circuit (default `5`)
* `DQ_RESET_TIMEOUT` – seconds to wait before closing the circuit again (default `30`)

Launch with Uvicorn:

```bash
DQ_GATEWAY=http://localhost:8000/rpc \
DQ_HOST=127.0.0.1 \
uvicorn peagen.worker:app --host 0.0.0.0 --port 8001
```

A Docker deployment follows the same pattern but uses the environment variables above in the container.

## Submitting Tasks

You can submit tasks directly via JSON‑RPC or through the Peagen CLI.

### Using JSON‑RPC

Send an HTTP POST to the gateway’s `/rpc` endpoint. Example to run the `process` handler:

```bash
curl -X POST http://localhost:8000/rpc \
  -H 'Content-Type: application/json' \
  -d '{
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {
            "pool": "default",
            "payload": {
                "action": "process",
                "projects_payload": "projects_payload.yaml"
            }
        },
        "id": "1"
      }'
```

### Using the Peagen CLI

The CLI wraps the JSON‑RPC calls for you. To enqueue a processing task and poll until it finishes:

```bash
peagen remote --gateway-url http://localhost:8000/rpc \
  process projects_payload.yaml --watch
```

Inspect tasks:

```bash
peagen remote --gateway-url http://localhost:8000/rpc task get <task-id>
```

---
Use this guide whenever you need to spin up a demo environment or troubleshoot deployments.
