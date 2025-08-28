"""Tests for runtime configuration environment variables."""

from importlib import reload

import pytest

from auto_authn import runtime_cfg


@pytest.mark.unit
def test_settings_build_from_urls(monkeypatch):
    """Settings should honor explicit Redis and Postgres URLs."""
    pg_url = "postgresql://user:pass@localhost:5432/db"
    redis_url = "redis://:password@localhost:6379/1"

    monkeypatch.setenv("POSTGRES_URL", pg_url)
    monkeypatch.setenv("REDIS_URL", redis_url)
    monkeypatch.delenv("ASYNC_FALLBACK_DB", raising=False)

    reload(runtime_cfg)
    settings = runtime_cfg.Settings()

    assert settings.pg_dsn == pg_url
    assert settings.apg_dsn == "postgresql+asyncpg://user:pass@localhost:5432/db"
    assert settings.redis_url == redis_url


@pytest.mark.unit
def test_apg_dsn_fallback(monkeypatch):
    """When Postgres is unset, apg_dsn falls back to ASYNC_FALLBACK_DB."""
    fallback = "sqlite+aiosqlite:///./gateway.db"

    monkeypatch.delenv("POSTGRES_URL", raising=False)
    monkeypatch.delenv("PG_DSN", raising=False)
    monkeypatch.delenv("PG_HOST", raising=False)
    monkeypatch.delenv("PG_DB", raising=False)
    monkeypatch.delenv("PG_USER", raising=False)
    monkeypatch.setenv("ASYNC_FALLBACK_DB", fallback)

    reload(runtime_cfg)
    settings = runtime_cfg.Settings()

    assert settings.pg_dsn == ""
    assert settings.apg_dsn == fallback
