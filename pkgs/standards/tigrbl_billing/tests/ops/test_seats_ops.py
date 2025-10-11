import pytest

from tigrbl_billing.ops import seats_ops
from tigrbl_billing.tables.seat_allocation import SeatState


@pytest.mark.asyncio
async def test_seat_assign_creates_active_allocation(recording_model):
    ctx = {}

    result = await seats_ops.seat_assign(
        subscription_item_id="sub_item_1",
        subject_ref="user:1",
        role="admin",
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    payload = recording_model.handlers.create.calls[0]["payload"]
    assert payload == {
        "subscription_item_id": "sub_item_1",
        "subject_ref": "user:1",
        "role": "admin",
        "state": SeatState.ACTIVE.name,
    }


@pytest.mark.asyncio
async def test_seat_release_marks_released(recording_model):
    ctx = {}

    await seats_ops.seat_release(
        seat_allocation_id="seat_1",
        model=recording_model,
        ctx=ctx,
    )

    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"seat_allocation_id": "seat_1"}
    assert call_ctx["payload"] == {"state": SeatState.RELEASED.name}


@pytest.mark.asyncio
async def test_seat_suspend_marks_suspended(recording_model):
    ctx = {}

    await seats_ops.seat_suspend(
        seat_allocation_id="seat_2",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {"state": SeatState.SUSPENDED.name}
