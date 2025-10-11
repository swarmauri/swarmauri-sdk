"""
API for a specific billing strategy, built with tigrbl + tigrbl_billing.
- Only tigrbl objects & patterns are used.
- CRUD & upsert use tigrbl default verbs (create/update/replace/merge/delete/list).
- Non-CRUD lifecycle ops are bound via @op_ctx(bind=...).
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem

from tigrbl_billing.tables.product import Product
from tigrbl_billing.tables.price import Price


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([Product, Price])
    return app


app = build_app(async_mode=True)
