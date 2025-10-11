from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl_billing.tables.customer_balance import CustomerBalance
from tigrbl_billing.tables.balance_top_off import BalanceTopOff
from tigrbl_billing.tables.credit_ledger import CreditLedger
from tigrbl_billing.ops import request_top_off, apply_top_off, check_and_top_off


@op_ctx(
    alias="request_top_off", target="custom", arity="collection", bind=CustomerBalance
)
def balance__request_top_off(cls, ctx):
    return request_top_off(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(alias="apply_top_off", target="custom", arity="collection", bind=BalanceTopOff)
def topoff__apply(cls, ctx):
    return apply_top_off(ctx, None, None, **(ctx.get("payload") or {}))


@op_ctx(
    alias="check_and_top_off", target="custom", arity="collection", bind=CustomerBalance
)
def balance__check_and_top_off(cls, ctx):
    return check_and_top_off(ctx, None, None, **(ctx.get("payload") or {}))


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([CustomerBalance, BalanceTopOff, CreditLedger])
    return app


app = build_app(async_mode=True)
