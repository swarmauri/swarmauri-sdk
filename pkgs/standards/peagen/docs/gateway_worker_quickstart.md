# Peagen Gateway & Worker Quickstart

This guide summarizes how to launch the gateway and a worker, then use the
Peagen CLI to log in, manage deploy keys, and store encrypted secrets. The
examples assume the services run locally.

## 1. Configure `.peagen.toml`

Create a minimal configuration in your working directory:

```toml
[queues]
# in-memory queue for testing
default_queue = "in_memory"

[result_backends]
# in-memory backend for testing
default_backend = "in_memory"
[result_backends.adapters.in_memory]
```

For production use Redis and Postgres as described in
`standards/peagen/AGENTS.md`.

## 2. Start the gateway

Run the gateway with Uvicorn. Environment variables control database and queue
settings:

```bash
uvicorn peagen.gateway:app --host 0.0.0.0 --port 8000
```

The gateway exposes `/rpc` for JSON-RPC requests and `/ws/tasks` for events.

## 3. Start a worker

Workers connect back to the gateway via JSON-RPC:

```bash
DQ_GATEWAY=http://localhost:8000/rpc \
DQ_HOST=127.0.0.1 \
uvicorn peagen.worker:app --host 0.0.0.0 --port 8001
```

Adjust `DQ_POOL` and `PORT` if running multiple workers.

## 4. Log in and upload your key

Generate a key pair and upload the public key to the gateway. Provide a
passphrase if desired:

```bash
peagen keys create --passphrase
peagen login --passphrase <PASS> --gateway-url http://localhost:8000/rpc
```

## 5. Store a deploy key

Save your private deploy key as an encrypted secret on the gateway so workers can
push commits:

```bash
peagen remote secrets add DEPLOY_KEY "$(cat ~/.ssh/id_rsa)" --gateway-url http://localhost:8000/rpc
```

On the worker, set the environment variable so pushes use the key:

```bash
export DEPLOY_KEY_SECRET=DEPLOY_KEY
```

## 6. Add other secrets

Encrypt arbitrary secrets locally, targeting the gateway and worker public keys:

```bash
peagen local secrets add OPENAI_API_KEY sk-... \
  --recipients /path/to/gateway_pub.asc \
  --recipients /path/to/worker_pub.asc
```

To store the secret directly on the gateway:

```bash
peagen remote secrets add OPENAI_API_KEY sk-... --gateway-url http://localhost:8000/rpc
```

You can now submit tasks with `peagen remote process` and the worker will fetch
secrets as needed.
