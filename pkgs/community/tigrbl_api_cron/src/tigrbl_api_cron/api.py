"""API construction helpers for the cron scheduler."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine

from .tables import CronJob, CronJobResult


def build_app(
    *, async_mode: bool = True, engine_cfg: dict[str, Any] | None = None
) -> TigrblApp:
    """Create a :class:`TigrblApp` with the cron job models registered."""

    if engine_cfg is None:
        fd, path = tempfile.mkstemp(prefix="tigrbl_api_cron_", suffix=".db")
        os.close(fd)
        cfg = {"kind": "sqlite", "async": async_mode, "path": path}
    else:
        cfg = engine_cfg
    app = TigrblApp(engine=build_engine(cfg))
    app.include_models([CronJob, CronJobResult], base_prefix="/cron")
    app.attach_diagnostics(prefix="/system")
    return app


app = build_app(async_mode=True)


__all__ = ["build_app", "app"]
