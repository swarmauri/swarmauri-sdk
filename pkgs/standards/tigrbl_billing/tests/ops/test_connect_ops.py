import pytest

from tigrbl_billing.ops import connect_ops


@pytest.mark.asyncio
async def test_refund_application_fee_sets_refunded_flag(recording_model):
    ctx = {}

    result = await connect_ops.refund_application_fee(
        application_fee_id="fee_123",
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"application_fee_id": "fee_123"}
    assert call_ctx["payload"] == {"refunded": True}
