
"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""
from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.usage_rollup import UsageRollup
from tigrbl_billing.ops import rollup_usage_periodic

@op_ctx(alias="rollup_periodic", target="custom", arity="collection", bind=UsageRollup)
def usage__rollup_periodic(cls, ctx):
    return rollup_usage_periodic(ctx, None, None, **(ctx.get("payload") or {}))

def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([UsageEvent, UsageRollup])
    return app

app = build_app(async_mode=True)
