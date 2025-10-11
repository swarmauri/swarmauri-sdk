import pytest

from tigrbl_billing.ops import subscription_ops
from tigrbl_billing.tables.subscription import SubscriptionStatus


@pytest.mark.asyncio
async def test_start_subscription_sets_trial_status_when_trial_end(recording_model):
    ctx = {}
    items = [{"price_id": "price_1", "quantity": 1}]

    result = await subscription_ops.start_subscription(
        customer_id="cus_1",
        items=items,
        trial_end="2024-01-31",
        metadata={"plan": "trial"},
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    payload = recording_model.handlers.create.calls[0]["payload"]
    assert payload["status"] == SubscriptionStatus.TRIALING.name
    assert payload["items"] == items
    assert payload["metadata"] == {"plan": "trial"}


@pytest.mark.asyncio
async def test_start_subscription_sets_active_without_trial(recording_model):
    ctx = {}

    await subscription_ops.start_subscription(
        customer_id="cus_2",
        items=[{"price_id": "price_2", "quantity": 2}],
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.create.calls[0]["payload"]
    assert payload["status"] == SubscriptionStatus.ACTIVE.name
    assert payload["cancel_at_period_end"] is False


@pytest.mark.asyncio
async def test_cancel_subscription_defers_cancellation(recording_model):
    ctx = {}

    await subscription_ops.cancel_subscription(
        subscription_id="sub_1",
        cancel_at_period_end=True,
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {"cancel_at_period_end": True}


@pytest.mark.asyncio
async def test_cancel_subscription_immediate(recording_model):
    ctx = {}

    await subscription_ops.cancel_subscription(
        subscription_id="sub_2",
        cancel_at_period_end=False,
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {
        "status": SubscriptionStatus.CANCELED.name,
        "cancel_at_period_end": False,
    }


@pytest.mark.asyncio
async def test_pause_subscription_marks_past_due(recording_model):
    ctx = {}

    await subscription_ops.pause_subscription(
        subscription_id="sub_3",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {"status": SubscriptionStatus.PAST_DUE.name}


@pytest.mark.asyncio
async def test_resume_subscription_clears_cancel_flag(recording_model):
    ctx = {}

    await subscription_ops.resume_subscription(
        subscription_id="sub_4",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {
        "status": SubscriptionStatus.ACTIVE.name,
        "cancel_at_period_end": False,
    }


@pytest.mark.asyncio
async def test_trial_start_sets_trialing_status(recording_model):
    ctx = {}

    await subscription_ops.trial_start(
        subscription_id="sub_5",
        trial_end="2024-02-01",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {
        "trial_end": "2024-02-01",
        "status": SubscriptionStatus.TRIALING.name,
    }


@pytest.mark.asyncio
async def test_trial_end_resumes_active_status(recording_model):
    ctx = {}

    await subscription_ops.trial_end(
        subscription_id="sub_6",
        model=recording_model,
        ctx=ctx,
    )

    payload = recording_model.handlers.update.calls[0]["payload"]
    assert payload == {"trial_end": None, "status": SubscriptionStatus.ACTIVE.name}


@pytest.mark.asyncio
async def test_proration_preview_echoes_inputs():
    preview = await subscription_ops.proration_preview(
        subscription_id="sub_7",
        proposed_items=[{"price_id": "price_3", "quantity": 1}],
        model=None,
        ctx=None,
    )

    assert preview == {
        "subscription_id": "sub_7",
        "preview": [{"price_id": "price_3", "quantity": 1}],
    }
