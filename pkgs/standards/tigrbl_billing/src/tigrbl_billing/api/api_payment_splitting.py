"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops load decorated helpers from ``tigrbl_billing.ops`` on demand.
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.split_rule import SplitRule
from tigrbl_billing.tables.application_fee import ApplicationFee

from tigrbl_billing import ops

# Register the payment splitting helper required by this API.
ops.refund_application_fee


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([SplitRule, ApplicationFee])
    return app


app = build_app(async_mode=True)
