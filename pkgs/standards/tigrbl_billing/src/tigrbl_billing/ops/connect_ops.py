from __future__ import annotations
from tigrbl import op_ctx
from tigrbl_billing.tables.application_fee import ApplicationFee


@op_ctx(
    alias="refund_app_fee",
    target="custom",
    arity="member",
    bind=ApplicationFee,
    persist="default",
)
async def refund_application_fee(*, application_fee_id, model=None, ctx=None, **_):
    ctx["path_params"] = {"application_fee_id": application_fee_id}
    ctx["payload"] = {"refunded": True}
    return await model.handlers.update.handler(ctx)
