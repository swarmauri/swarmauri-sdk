## Auto KMS

Auto KMS provides a lightweight key management service built on FastAPI. 

### Deploy

Run the service with the provided CLI:

```bash
uv run --package auto_kms --directory pkgs/standards/auto_kms auto-kms serve --host 127.0.0.1 --port 8000 --no-reload
```

### Verify

Once the service starts, you can verify it is running:

```bash
curl http://127.0.0.1:8000/healthz
```

The endpoint returns `{"status": "alive"}` when deployment succeeds.
