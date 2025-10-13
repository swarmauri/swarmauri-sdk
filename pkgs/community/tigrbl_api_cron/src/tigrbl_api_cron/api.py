"""API construction helpers for the cron scheduler."""

from __future__ import annotations

from typing import Any

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from .tables import CronJob, CronJobResult


def build_app(
    *, async_mode: bool = True, engine_cfg: dict[str, Any] | None = None
) -> TigrblApp:
    """Create a :class:`TigrblApp` with the cron job models registered."""

    cfg = engine_cfg or mem(async_=async_mode)
    app = TigrblApp(engine=build_engine(cfg))
    app.include_models([CronJob, CronJobResult], base_prefix="/cron")
    app.attach_diagnostics(prefix="/system")
    return app


app = build_app(async_mode=True)


__all__ = ["build_app", "app"]
