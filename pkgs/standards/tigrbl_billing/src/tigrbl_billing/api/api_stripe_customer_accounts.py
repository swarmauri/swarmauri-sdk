"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.customer import Customer
from tigrbl_billing.ops import create_or_link_customer, attach_payment_method


@op_ctx(alias="create_or_link", target="custom", arity="collection", bind=Customer)
def customer__create_or_link(cls, ctx):
    return create_or_link_customer(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(
    alias="attach_payment_method", target="custom", arity="collection", bind=Customer
)
def customer__attach_payment_method(cls, ctx):
    return attach_payment_method(ctx, None, None, **(ctx.get("payload") or {}))


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Customer])
    return app


app = build_app(async_mode=True)
