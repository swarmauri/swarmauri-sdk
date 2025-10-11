from __future__ import annotations
from tigrbl import op_ctx
from tigrbl_billing.tables.payment_intent import PaymentIntent, PaymentIntentStatus


@op_ctx(
    alias="capture",
    target="custom",
    arity="member",
    bind=PaymentIntent,
    persist="default",
)
async def capture_payment_intent(*, payment_intent_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"payment_intent_id": payment_intent_id}
    ctx["payload"] = {"status": PaymentIntentStatus.SUCCEEDED.name}
    return await model.handlers.update.handler(ctx)


@op_ctx(
    alias="cancel",
    target="custom",
    arity="member",
    bind=PaymentIntent,
    persist="default",
)
async def cancel_payment_intent(*, payment_intent_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"payment_intent_id": payment_intent_id}
    ctx["payload"] = {"status": PaymentIntentStatus.CANCELED.name}
    return await model.handlers.update.handler(ctx)
