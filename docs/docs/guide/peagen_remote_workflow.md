# Remote DOE Process and Evolve Workflow

This guide explains how to run a DOE process remotely using the public gateway and then launch an evolve job. The gateway URL used throughout is `https://gw.peagen.com`.

1. **Login to the gateway**
   ```bash
   peagen login --gateway-url https://gw.peagen.com
   ```
2. **Fetch the server key**
   ```bash
   peagen keys fetch-server --gateway-url https://gw.peagen.com
   ```
3. **Submit a DOE processing task**
   ```bash
   peagen remote --gateway-url https://gw.peagen.com \
     doe process SPEC.yaml TEMPLATE.yaml --watch
   ```
   The command prints a `taskId` once submitted and streams status updates while `--watch` is active.
4. **Run an evolve job**
   ```bash
   peagen remote --gateway-url https://gw.peagen.com \
     evolve EVOLVE_SPEC.yaml --watch
   ```
5. **Check task status**
   ```bash
   peagen remote --gateway-url https://gw.peagen.com task get <taskId>
   ```
6. **Fetch generated artifacts**
   ```bash
   peagen fetch WORKSPACE_URI
   ```
   Replace `WORKSPACE_URI` with the URI returned by the evolve job.

A successful run will report `"status": "success"` and the fetched workspace should contain the expected artifacts.
