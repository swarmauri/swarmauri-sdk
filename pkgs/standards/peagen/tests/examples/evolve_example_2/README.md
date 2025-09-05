# Evolve Example 2

This example demonstrates running the `peagen evolve` command both locally and through a gateway.

The `cfg` directory contains two example configuration files:

- `local.toml` – uses the in-memory queue and filesystem storage for quick local runs.
- `remote.toml` – expects Redis, PostgreSQL and MinIO credentials in the environment for remote execution via the gateway.
