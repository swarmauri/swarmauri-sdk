"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

# Import ops module to ensure op_ctx registrations for included tables.
from tigrbl_billing import ops as _ops  # noqa: F401

from tigrbl_billing.tables.usage_event import UsageEvent


# Metered usage ingest uses default create on UsageEvent.
def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([UsageEvent])
    return app


app = build_app(async_mode=True)
