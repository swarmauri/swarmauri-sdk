FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -U pip uv

RUN uv venv /tmp/.venv
ENV UV_PROJECT_ENVIRONMENT=/tmp/.venv

WORKDIR /docs

EXPOSE 8000

# The compose file binds the docs/ directory at runtime.
# Dependencies are installed via `uv sync` in the service command.

CMD ["bash", "-lc", "uv --version && python --version"]

