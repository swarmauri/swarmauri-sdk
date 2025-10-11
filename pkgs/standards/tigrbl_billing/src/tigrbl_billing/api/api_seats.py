"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.seat_allocation import SeatAllocation
from tigrbl_billing.ops import seat_assign, seat_release, seat_suspend


@op_ctx(alias="assign", target="custom", arity="collection", bind=SeatAllocation)
def seat__assign(cls, ctx):
    return seat_assign(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="release", target="custom", arity="collection", bind=SeatAllocation)
def seat__release(cls, ctx):
    return seat_release(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="suspend", target="custom", arity="collection", bind=SeatAllocation)
def seat__suspend(cls, ctx):
    return seat_suspend(ctx, None, None, **(ctx.get("payload") or {}))


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([SeatAllocation])
    return app


app = build_app(async_mode=True)
