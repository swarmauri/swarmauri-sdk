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

# ─────────────────── install Python deps with uv  ──────────────────
WORKDIR /app

# 1. Copy only dependency-defining files first (better layer caching)
COPY ./pkgs/ ./pkgs/

RUN uv pip install --directory pkgs/standards/peagen --system .

# ────────────────── runtime configuration  ─────────────────────────
EXPOSE 8000

ENV \
    PEAGEN_POOL=""\
    PEAGEN_GATEWAY=""\
    PG_PORT="5432"

CMD ["python", "-m", "peagen.worker"]
