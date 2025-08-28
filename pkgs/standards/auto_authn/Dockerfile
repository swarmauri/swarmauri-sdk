# ───────────────────────── base image ──────────────────────────────
FROM python:3.12-slim

# ─────────────────── system deps + uv package manager ──────────────
RUN apt-get update && \
    apt-get install --yes --no-install-recommends build-essential git && \
    pip install --no-cache-dir uv && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# ─────────────────── dependency installation ───────────────────────
# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY ./pkgs/ ./pkgs/

# ─────────────────── application code ──────────────────────────────

RUN uv pip install --directory pkgs/standards/auto_authn --system .[postgres]

# ────────────────── runtime configuration  ─────────────────────────
EXPOSE 8000

ENV \
    PG_HOST="" \
    PG_PORT="5432" \
    PG_DB="" \
    PG_USER="" \
    PG_PASS="" \
    REDIS_HOST="" \
    REDIS_PASSWORD=""
    
CMD ["sh", "-c", "python -c 'import uvicorn; uvicorn.run(\"auto_authn.app:app\", host=\"0.0.0.0\", port=8000, log_level=\"info\", proxy_headers=True, forwarded_allow_ips=\"*\")'"]
