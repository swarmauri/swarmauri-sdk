import pytest

from tigrbl_billing.ops import credit_usage_ops
from tigrbl_billing.tables.credit_ledger import LedgerDirection


@pytest.mark.asyncio
async def test_charge_credits_emits_debit_entry(recording_model):
    ctx = {}

    result = await credit_usage_ops.charge_credits(
        usage_event_id="evt_1",
        customer_id="cus_1",
        feature_key="messages",
        quantity=3,
        currency="usd",
        metadata={"tier": "pro"},
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.create.calls[0]
    assert call_ctx["payload"] == {
        "usage_event_id": "evt_1",
        "customer_id": "cus_1",
        "feature_key": "messages",
        "quantity": 3,
        "currency": "usd",
        "direction": LedgerDirection.DEBIT.name,
        "metadata": {"tier": "pro"},
    }
