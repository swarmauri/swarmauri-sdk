from __future__ import annotations
from tigrbl import op_ctx
from tigrbl_billing.tables.credit_ledger import LedgerDirection
from tigrbl_billing.tables.usage_event import UsageEvent

@op_ctx(alias="charge_credits", target="custom", arity="collection", bind=UsageEvent, persist="default")
async def charge_credits(*, usage_event_id, customer_id, feature_key: str, quantity: int, currency: str, metadata: dict | None=None, model=None, ctx=None, **_):
    # Domain compute belongs in schema/validators; op emits a ledger debit intent.
    ctx['payload'] = {
        'usage_event_id': usage_event_id,
        'customer_id': customer_id,
        'feature_key': feature_key,
        'quantity': int(quantity),
        'currency': currency,
        'direction': LedgerDirection.DEBIT.name,
        'metadata': metadata or {},
    }
    # Let the model's create handler (likely on CreditLedger via schema include) persist the entry.
    return await model.handlers.create.handler(ctx)
