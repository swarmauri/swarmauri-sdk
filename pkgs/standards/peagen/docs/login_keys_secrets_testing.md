# Testing `peagen` public key, deploy key, and secrets

This note describes how to verify that the `publickey`, `deploykey`, and `secrets` CLI commands interact with a running gateway and worker using a Postgres backend.

1. Start Postgres and Redis locally and create a minimal `.peagen.toml` pointing to them.
2. Launch the gateway:
   ```bash
   uvicorn peagen.gateway:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"
   ```
3. Launch a worker in a separate shell:
   ```bash
   uvicorn peagen.worker:app --host 0.0.0.0 --port 8001
   ```
4. Upload your public key and view available deploy keys:
   ```bash
   peagen remote publickey upload --gateway-url http://localhost:8000/rpc
   peagen local deploykey list
   ```
5. Add a secret via the gateway and confirm it in Postgres:
   ```bash
   peagen remote -q --gateway-url http://localhost:8000/rpc secrets add demo-secret supersecret
   sudo -u postgres psql -d peagen_db -c "SELECT name FROM secrets;"
   ```
6. Retrieve and remove the secret:
   ```bash
   peagen remote -q --gateway-url http://localhost:8000/rpc secrets get demo-secret
   peagen remote -q --gateway-url http://localhost:8000/rpc secrets remove demo-secret
   ```

The secret appears in the `secrets` table after uploading and is removed once deleted.
