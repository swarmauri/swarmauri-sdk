
"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""
from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.subscription import Subscription
from tigrbl_billing.ops import trial_start, trial_end, proration_preview

@op_ctx(alias="trial_start", target="custom", arity="collection", bind=Subscription)
def subscription__trial_start(cls, ctx):
    return trial_start(ctx, None, None, **(ctx.get("payload") or {}))

@op_ctx(alias="trial_end", target="custom", arity="collection", bind=Subscription)
def subscription__trial_end(cls, ctx):
    return trial_end(ctx, None, None, **(ctx.get("payload") or {}))

@op_ctx(alias="proration_preview", target="custom", arity="collection", bind=Subscription)
def subscription__proration_preview(cls, ctx):
    return proration_preview(ctx, None, None, **(ctx.get("payload") or {}))

def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Subscription])
    return app

app = build_app(async_mode=True)
