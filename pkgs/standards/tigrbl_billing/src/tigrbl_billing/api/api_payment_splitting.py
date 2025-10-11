"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.split_rule import SplitRule
from tigrbl_billing.tables.application_fee import ApplicationFee
from tigrbl_billing.ops import refund_application_fee


@op_ctx(
    alias="refund_app_fee", target="custom", arity="collection", bind=ApplicationFee
)
def application_fee__refund(cls, ctx):
    return refund_application_fee(ctx, None, None, **(ctx.get("payload") or {}))


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([SplitRule, ApplicationFee])
    return app


app = build_app(async_mode=True)
