"""Simple secret resolution utilities."""

from __future__ import annotations

import os


def resolve_secret_ref(secret_ref: str) -> str:
    """Resolve ``secret_ref`` using installed plugins or environment variables."""
    provider, _, name = secret_ref.partition(":")
    # Try dynamic import of peagen's plugin manager; ignore if unavailable
    try:
        from peagen._utils.config_loader import load_peagen_toml  # type: ignore
        from peagen.plugins import PluginManager  # type: ignore
    except Exception:  # peagen not installed
        if provider and provider != "env":
            raise RuntimeError("Secret providers require peagen to be installed")
        value = os.getenv(name)
        if value is None:
            raise KeyError(f"Environment variable {name} not set")
        return value

    cfg = load_peagen_toml()
    pm = PluginManager(cfg)
    secret_plugin = pm.get("secrets", provider or None)
    return secret_plugin.get(name)


__all__ = ["resolve_secret_ref"]
