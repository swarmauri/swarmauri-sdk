from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import engine as build_engine, mem
from tigrbl_billing.tables.customer_balance import CustomerBalance
from tigrbl_billing.tables.balance_top_off import BalanceTopOff
from tigrbl_billing.tables.credit_ledger import CreditLedger

from tigrbl_billing import ops

# Register the balance top-off operations required by this API.
ops.request_top_off
ops.apply_top_off
ops.check_and_top_off


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=build_engine(mem(async_=async_mode)))
    app.include_models([CustomerBalance, BalanceTopOff, CreditLedger])
    return app


app = build_app(async_mode=True)
