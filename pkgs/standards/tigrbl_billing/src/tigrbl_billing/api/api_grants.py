
from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl_billing.tables.credit_grant import CreditGrant
from tigrbl_billing.tables.credit_ledger import CreditLedger
from tigrbl_billing.ops import apply_grant, revoke_grant

@op_ctx(alias="apply_grant", target="custom", arity="collection", bind=CreditGrant)
def grants__apply(cls, ctx):
    return apply_grant(ctx, None, None, **(ctx.get("payload") or {}))

@op_ctx(alias="revoke_grant", target="custom", arity="collection", bind=CreditGrant)
def grants__revoke(cls, ctx):
    return revoke_grant(ctx, None, None, **(ctx.get("payload") or {}))

def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([CreditGrant, CreditLedger])
    return app

app = build_app(async_mode=True)
