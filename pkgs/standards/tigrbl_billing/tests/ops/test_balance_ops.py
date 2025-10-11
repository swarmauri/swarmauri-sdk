import pytest

from tigrbl_billing.ops import balance_ops
from tigrbl_billing.tables.balance_top_off import (
    TopOffMethod,
    TopOffStatus,
    TopOffTrigger,
)


@pytest.mark.asyncio
async def test_request_top_off_populates_payload(recording_model, blank_ctx):
    ctx = {**blank_ctx}

    result = await balance_ops.request_top_off(
        balance_id="bal_123",
        amount="42",
        currency="usd",
        trigger="manual",
        method="payment_intent",
        metadata={"source": "unit"},
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.create.calls[0]
    assert call_ctx["payload"]["amount"] == 42
    assert call_ctx["payload"]["trigger"] == TopOffTrigger.MANUAL.name
    assert call_ctx["payload"]["method"] == TopOffMethod.PAYMENT_INTENT.name
    assert call_ctx["payload"]["status"] == TopOffStatus.INITIATED.name
    assert call_ctx["payload"]["metadata"] == {"source": "unit"}


@pytest.mark.asyncio
async def test_check_and_top_off_returns_intent():
    response = await balance_ops.check_and_top_off(
        balance_id="bal_456", model=None, ctx={}
    )
    assert response == {"balance_id": "bal_456", "top_off_created": False}


@pytest.mark.asyncio
async def test_apply_top_off_requires_identifier(recording_model, blank_ctx):
    with pytest.raises(ValueError):
        await balance_ops.apply_top_off(model=recording_model, ctx={**blank_ctx})


@pytest.mark.asyncio
async def test_apply_top_off_uses_update_handler(recording_model, blank_ctx):
    ctx = {"path_params": {"top_off_id": "top_1"}}

    result = await balance_ops.apply_top_off(
        status="FAILED",
        failure_reason="insufficient_funds",
        processed_at="2024-01-01T00:00:00Z",
        metadata={"attempt": 1},
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"top_off_id": "top_1"}
    assert call_ctx["payload"]["status"] == "FAILED"
    assert call_ctx["payload"]["failure_reason"] == "insufficient_funds"
    assert call_ctx["payload"]["processed_at"] == "2024-01-01T00:00:00Z"
    assert call_ctx["payload"]["metadata"] == {"attempt": 1}
