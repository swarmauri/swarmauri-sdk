from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl_billing.tables.credit_usage_policy import CreditUsagePolicy
from tigrbl_billing.tables.usage_event import UsageEvent
from tigrbl_billing.tables.credit_ledger import CreditLedger

from tigrbl_billing import ops

# Register the credit usage operation for this API.
ops.charge_credits


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([CreditUsagePolicy, UsageEvent, CreditLedger])
    return app


app = build_app(async_mode=True)
