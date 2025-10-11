import pytest

from tigrbl_billing.ops import customer_ops


@pytest.mark.asyncio
async def test_create_or_link_customer_normalizes_tax_exempt(recording_model):
    ctx = {}

    result = await customer_ops.create_or_link_customer(
        email="user@example.com",
        name="User",
        stripe_customer_id="cus_1",
        default_payment_method_ref="pm_1",
        tax_exempt="reverse",
        metadata={"segment": "beta"},
        active=False,
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.merge.calls[0]
    assert call_ctx["payload"]["tax_exempt"] == "REVERSE"
    assert call_ctx["payload"]["active"] is False


@pytest.mark.asyncio
async def test_create_or_link_customer_defaults_missing_metadata(recording_model):
    ctx = {}

    await customer_ops.create_or_link_customer(
        email="user@example.com",
        name="User",
        tax_exempt="invalid",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.merge.calls[0]["payload"]
    assert payload["tax_exempt"] == "NONE"
    assert payload["metadata"] == {}


@pytest.mark.asyncio
async def test_attach_payment_method_sets_path_and_payload(recording_model):
    ctx = {}

    result = await customer_ops.attach_payment_method(
        customer_id="cus_9",
        payment_method_ref="pm_9",
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"customer_id": "cus_9"}
    assert call_ctx["payload"] == {"default_payment_method_ref": "pm_9"}
