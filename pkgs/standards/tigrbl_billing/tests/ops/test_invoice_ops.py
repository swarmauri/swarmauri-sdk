import pytest

from tigrbl_billing.ops import invoice_ops
from tigrbl_billing.tables.invoice import InvoiceStatus


@pytest.mark.asyncio
async def test_finalize_invoice_sets_open_status(recording_model):
    ctx = {}
    items = [{"description": "Service", "amount": 1000}]

    result = await invoice_ops.finalize_invoice(
        invoice_id="inv_1",
        line_items=items,
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"invoice_id": "inv_1"}
    assert call_ctx["payload"]["status"] == InvoiceStatus.OPEN.name
    assert call_ctx["payload"]["line_items"] == items


@pytest.mark.asyncio
async def test_void_invoice_marks_void(recording_model):
    ctx = {}

    await invoice_ops.void_invoice(invoice_id="inv_2", model=recording_model, ctx=ctx)

    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["payload"] == {"status": InvoiceStatus.VOID.name}


@pytest.mark.asyncio
async def test_mark_invoice_uncollectible_updates_status(recording_model):
    ctx = {}

    await invoice_ops.mark_invoice_uncollectible(
        invoice_id="inv_3",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {"status": InvoiceStatus.UNCOLLECTIBLE.name}
