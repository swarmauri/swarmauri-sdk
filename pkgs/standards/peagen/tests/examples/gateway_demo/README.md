This example demonstrates a minimal setup for running the Peagen gateway and worker in a local development environment.

## Quickstart

1. Start the gateway:

   ```bash
   uvicorn peagen.gateway:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
   ```

2. Launch a worker connected to the gateway:

   ```bash
   PEAGEN_GATEWAY=http://127.0.0.1:8000/rpc \
   uvicorn peagen.worker:app --host 0.0.0.0 --port 8001
   ```

3. Create a new Git repository using the Peagen CLI:

   ```bash
   uv run --package peagen --directory pkgs/standards/peagen \
     peagen init project demo_repo --git-remote file://$(pwd)/remote_repo.git
   ```

4. Submit a mutate task through the gateway to modify the repository:

   ```bash
   uv run --package peagen --directory pkgs/standards/peagen \
     peagen remote -q --gateway-url http://127.0.0.1:8000/rpc \
     mutate doe_spec.yaml --repo ./demo_repo
   ```

5. Fetch the updated workspace back locally:

   ```bash
   uv run --package peagen --directory pkgs/standards/peagen \
     peagen remote -q --gateway-url http://127.0.0.1:8000/rpc \
     fetch --repo ./demo_repo --ref HEAD --out-dir ./workspace
   ```

   The command prints a JSON summary including the commit SHA and whether the
   repository was updated:

   ```text
   {"workspace": "./workspace", "commit": "<sha>", "updated": true}
   ```

Files in this directory:

* `doe_spec.yaml` - Design-of-experiments specification used to generate project payloads.
* `template_project.yaml` - Base project template consumed by the DOE process.
* `.peagen.toml` - Minimal configuration that uses in-memory queues and the local filesystem for results and artifacts.

Use these files when starting the gateway and worker or when submitting a DOE processing task via `peagen remote`.
