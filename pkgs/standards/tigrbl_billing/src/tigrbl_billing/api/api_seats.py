"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops load decorated helpers from ``tigrbl_billing.ops`` on demand.
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.seat_allocation import SeatAllocation

from tigrbl_billing import ops

# Register the seat allocation helpers required by this API.
ops.seat_assign
ops.seat_release
ops.seat_suspend


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([SeatAllocation])
    return app


app = build_app(async_mode=True)
