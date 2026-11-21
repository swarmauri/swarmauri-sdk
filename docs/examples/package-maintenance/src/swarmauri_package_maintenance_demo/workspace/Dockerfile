FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv
WORKDIR /workspace
COPY fixture/ pkgs/maintenance-demo/
RUN uv sync --directory pkgs/maintenance-demo
ENV UV_OFFLINE=1 PYTHONUNBUFFERED=1
CMD ["sleep", "infinity"]
