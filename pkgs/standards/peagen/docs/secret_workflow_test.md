# Peagen Secret Workflow Test

This document records the steps to verify `peagen` CLI public key, deploy key, and secret management against a Postgres-backed gateway. It demonstrates that secrets are persisted to the database and retrieved by a worker.

## Environment Setup

```bash
export PG_DSN="postgresql://peagen:peagen@localhost:5432/peagen"
export REDIS_URL="redis://localhost:6379/0"
uvicorn peagen.gateway:app --host 127.0.0.1 --port 8000 --proxy-headers --forwarded-allow-ips="*" &
PEAGEN_GATEWAY=http://127.0.0.1:8000/rpc uvicorn peagen.worker:app --host 127.0.0.1 --port 8001 &
```

A `.peagen.toml` referencing Redis and Postgres was placed in `/tmp/peagen_demo`.

## Key Generation and Public Key Upload

```bash
peagen local deploykey create --key-dir /tmp/peagen_demo/keys
peagen remote publickey upload --gateway-url http://127.0.0.1:8000/rpc --key-dir /tmp/peagen_demo/keys
```

The upload command succeeded, but `public_keys` remained empty as the gateway stores trusted keys in memory only.

## Secret Management

A tenant row for the `default` pool was inserted manually so the gateway could store secrets:

```sql
INSERT INTO tenants (slug, name, id, date_created, last_modified)
VALUES ('default', 'Default', '916180a7-0b43-5c08-b3c8-c738826880bb', NOW(), NOW());
```

Secrets were then added and retrieved via the worker:

```bash
peagen remote --gateway-url http://127.0.0.1:8000/rpc secrets add demo-secret secret_value --pool default
peagen remote --gateway-url http://127.0.0.1:8000/rpc secrets get demo-secret --pool default
```

The `secrets` table now contains the encrypted secret.

## Conclusion

`peagen` successfully stored secrets in Postgres once the tenant existed. Workers retrieved the secret through the `remote secrets get` command. Public keys uploaded during `peagen remote publickey upload` were not persisted to Postgres in this setup.
