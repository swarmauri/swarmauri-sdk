import pytest

from tigrbl_billing.ops import payment_ops
from tigrbl_billing.tables.payment_intent import PaymentIntentStatus


@pytest.mark.asyncio
async def test_capture_payment_intent_marks_succeeded(recording_model):
    ctx = {}

    result = await payment_ops.capture_payment_intent(
        payment_intent_id="pi_1",
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {"status": PaymentIntentStatus.SUCCEEDED.name}


@pytest.mark.asyncio
async def test_cancel_payment_intent_marks_canceled(recording_model):
    ctx = {}

    await payment_ops.cancel_payment_intent(
        payment_intent_id="pi_2",
        model=recording_model,
        ctx=ctx,
    )

    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"payment_intent_id": "pi_2"}
    assert call_ctx["payload"] == {"status": PaymentIntentStatus.CANCELED.name}
