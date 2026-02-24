from __future__ import annotations
from typing import Optional, Sequence, Mapping
from tigrbl import op_ctx
from tigrbl_billing.tables.subscription import Subscription, SubscriptionStatus


@op_ctx(
    alias="start",
    target="custom",
    arity="collection",
    bind=Subscription,
    persist="default",
)
async def start_subscription(
    *,
    customer_id,
    items: Sequence[Mapping[str, object]],
    collection_method: str = "charge_automatically",
    days_until_due: Optional[int] = None,
    trial_end: Optional[object] = None,
    external_id: Optional[str] = None,
    stripe_subscription_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    model=None,
    ctx=None,
    **_,
) -> dict:
    ctx["payload"] = {
        "customer_id": customer_id,
        "status": (
            SubscriptionStatus.TRIALING.name
            if trial_end
            else SubscriptionStatus.ACTIVE.name
        ),
        "cancel_at_period_end": False,
        "current_period_start": None,
        "current_period_end": None,
        "trial_end": trial_end,
        "collection_method": collection_method,
        "days_until_due": days_until_due,
        "external_id": external_id or stripe_subscription_id,
        "metadata": metadata or {},
        "items": list(items),
    }
    return await model.handlers.create.handler(ctx)


@op_ctx(
    alias="cancel",
    target="custom",
    arity="member",
    bind=Subscription,
    persist="default",
)
async def cancel_subscription(
    *, subscription_id, cancel_at_period_end: bool = True, model=None, ctx=None, **_
):
    ctx["path_params"] = {"subscription_id": subscription_id}
    if cancel_at_period_end:
        ctx["payload"] = {"cancel_at_period_end": True}
    else:
        ctx["payload"] = {
            "status": SubscriptionStatus.CANCELED.name,
            "cancel_at_period_end": False,
        }
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="pause", target="custom", arity="member", bind=Subscription, persist="default"
)
async def pause_subscription(*, subscription_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"subscription_id": subscription_id}
    ctx["payload"] = {"status": SubscriptionStatus.PAST_DUE.name}
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="resume",
    target="custom",
    arity="member",
    bind=Subscription,
    persist="default",
)
async def resume_subscription(*, subscription_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"subscription_id": subscription_id}
    ctx["payload"] = {
        "status": SubscriptionStatus.ACTIVE.name,
        "cancel_at_period_end": False,
    }
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="trial_start",
    target="custom",
    arity="member",
    bind=Subscription,
    persist="default",
)
async def trial_start(*, subscription_id, trial_end, model=None, ctx=None, **_):
    ctx["path_params"] = {"subscription_id": subscription_id}
    ctx["payload"] = {
        "trial_end": trial_end,
        "status": SubscriptionStatus.TRIALING.name,
    }
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="trial_end",
    target="custom",
    arity="member",
    bind=Subscription,
    persist="default",
)
async def trial_end(*, subscription_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"subscription_id": subscription_id}
    ctx["payload"] = {"trial_end": None, "status": SubscriptionStatus.ACTIVE.name}
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="proration_preview",
    target="custom",
    arity="member",
    bind=Subscription,
    persist="skip",
)
async def proration_preview(
    *,
    subscription_id,
    proposed_items: Sequence[Mapping[str, object]],
    model=None,
    ctx=None,
    **_,
):
    # pure compute; no persistence
    return {"subscription_id": str(subscription_id), "preview": list(proposed_items)}
