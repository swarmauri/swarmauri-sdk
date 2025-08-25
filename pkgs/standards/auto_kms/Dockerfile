# ────────────── base image ───────────────
FROM python:3.12-slim

# ────────── system deps + uv package manager ─────────
RUN apt-get update && \
    apt-get install --yes --no-install-recommends build-essential git && \
    pip install --no-cache-dir uv && \
    apt-get purge -y build-essential && \
    apt-get autoremove -y && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# ─────────── dependency installation ─────────
WORKDIR /app

# Copy dependency files first for better layer caching
COPY ./pkgs/ ./pkgs/

# Install the auto_kms package and its dependencies
RUN uv pip install --directory pkgs/standards/auto_kms --system .

# ────────── runtime configuration  ────────
EXPOSE 8003
ENV KMS_DATABASE_URL=""

CMD ["python", "-m", "auto_kms"]
