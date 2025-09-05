# Simple Evolve Demo

This example provides a minimal workspace and evolve specification for testing the `peagen evolve` command.
The workspace now includes a deliberately inefficient `bad_sort` function so
that mutations can attempt to improve its performance.
Winning mutants are committed to the repository when a VCS is configured. The task result includes the commit SHA and a `winner_oid` with the blob object ID for the mutated file.

## Local execution

Run the spec locally using the `local` subcommand:

```bash
PEAGEN_GATEWAY=http://127.0.0.1:8000/rpc \
uv run --package peagen --directory pkgs/standards/peagen \
  peagen local -q evolve tests/examples/simple_evolve_demo/evolve_spec_local.yaml
```

This writes the result JSON next to the spec file.

## Remote execution

Start a gateway and worker and then submit the job remotely:

```bash
uv run --package peagen --directory pkgs/standards/peagen \
  peagen remote -q --gateway-url http://127.0.0.1:8000/rpc \
  evolve tests/examples/simple_evolve_demo/evolve_remote_spec.yaml
```

You can fetch the task result with:

```bash
uv run --package peagen --directory pkgs/standards/peagen \
  peagen remote -q --gateway-url http://127.0.0.1:8000/rpc \
  task get <task-id>
```
