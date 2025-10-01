# ───────────────────────── base image ──────────────────────────────
FROM python:3.12-slim

# ─────────────────── system deps + uv package manager ──────────────
RUN apt-get update && \
    apt-get install --yes --no-install-recommends build-essential git python3-venv && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir uv && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Ensure non-root users can install additional dependencies at runtime.
RUN chmod -R a+rwX /opt/venv

# ─────────────────── install Python deps with uv  ──────────────────
WORKDIR /app

# 1. Copy only dependency-defining files first (better layer caching)
COPY ./pkgs/ /pkgs

RUN uv pip install --directory /pkgs/community/zdx . && \
    zdx install --manifest /pkgs/community/zdx/api_manifest.yaml

EXPOSE 8000

WORKDIR /docs

CMD ["zdx", "serve", "--generate", "--docs-dir", "/docs", "--manifest", "api_manifest.yaml", "--changed-only"]
