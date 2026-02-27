from tigrbl import TigrblApp
from tigrbl.shortcuts.engine import engine, mem

from tigrbl_billing import ops
from tigrbl_billing.tables.credit_grant import CreditGrant
from tigrbl_billing.tables.credit_ledger import CreditLedger

# Ensure only the grant-specific operations are registered for this API.
ops.apply_grant
ops.revoke_grant


def build_app(async_mode: bool = True) -> TigrblApp:
    app = TigrblApp(engine=engine(mem(async_=async_mode)))
    app.include_models([CreditGrant, CreditLedger])
    return app


app = build_app(async_mode=True)
