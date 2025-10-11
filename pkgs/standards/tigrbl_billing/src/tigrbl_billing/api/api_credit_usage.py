
from tigrbl import TigrblApp, op_ctx
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl_billing.tables.credit_usage_policy import CreditUsagePolicy
from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.credit_ledger import CreditLedger
from tigrbl_billing.ops import charge_credits

@op_ctx(alias="charge_credits", target="custom", arity="collection", bind=UsageEvent)
def usage__charge_credits(cls, ctx):
    return charge_credits(ctx, None, None, **(ctx.get("payload") or {}))

def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([CreditUsagePolicy, UsageEvent, CreditLedger])
    return app

app = build_app(async_mode=True)
