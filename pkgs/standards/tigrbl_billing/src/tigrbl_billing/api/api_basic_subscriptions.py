
"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""
from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.subscription import Subscription
from tigrbl_billing.tables.subscription_item import SubscriptionItem
from tigrbl_billing.ops import start_subscription, cancel_subscription, pause_subscription, resume_subscription

@op_ctx(alias="start", target="custom", arity="collection", bind=Subscription)
def subscription__start(cls, ctx):
    return start_subscription(ctx, None, None, **(ctx.get("payload") or {}))

@op_ctx(alias="cancel", target="custom", arity="collection", bind=Subscription)
def subscription__cancel(cls, ctx):
    return cancel_subscription(ctx, None, None, **(ctx.get("payload") or {}))

@op_ctx(alias="pause", target="custom", arity="collection", bind=Subscription)
def subscription__pause(cls, ctx):
    return pause_subscription(ctx, None, None, **(ctx.get("payload") or {}))

@op_ctx(alias="resume", target="custom", arity="collection", bind=Subscription)
def subscription__resume(cls, ctx):
    return resume_subscription(ctx, None, None, **(ctx.get("payload") or {}))

def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Subscription, SubscriptionItem])
    return app

app = build_app(async_mode=True)
