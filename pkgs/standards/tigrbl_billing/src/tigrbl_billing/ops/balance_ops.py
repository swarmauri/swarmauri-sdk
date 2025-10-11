from __future__ import annotations
from tigrbl import op_ctx
from tigrbl_billing.tables.balance_top_off import (
    BalanceTopOff,
    TopOffTrigger,
    TopOffMethod,
    TopOffStatus,
)
from tigrbl_billing.tables.customer_balance import CustomerBalance


@op_ctx(
    alias="request_top_off",
    target="custom",
    arity="collection",
    bind=CustomerBalance,
    persist="default",
)
async def request_top_off(
    *,
    balance_id,
    amount: int,
    currency: str,
    trigger: str = "manual",
    method: str = "payment_intent",
    metadata: dict | None = None,
    model=None,
    ctx=None,
    **_,
) -> dict:
    ctx["payload"] = {
        "balance_id": balance_id,
        "amount": int(amount),
        "currency": currency,
        "trigger": TopOffTrigger[trigger.upper()].name,
        "method": TopOffMethod[method.upper()].name,
        "status": TopOffStatus.INITIATED.name,
        "metadata": metadata or {},
    }
    # Top-off requests are modeled as a child resource in schema; use create
    return await model.handlers.create.handler(ctx)


@op_ctx(
    alias="check_and_top_off",
    target="custom",
    arity="member",
    bind=CustomerBalance,
    persist="skip",
)
async def check_and_top_off(*, balance_id, model=None, ctx=None, **_) -> dict:
    # No direct DB checks here; leave policy enforcement to background/cron or schema-level rules.
    # This op just signals intent; persistence is handled elsewhere.
    return {"balance_id": str(balance_id), "top_off_created": False}


@op_ctx(
    alias="apply_top_off",
    target="custom",
    arity="member",
    bind=BalanceTopOff,
    persist="default",
)
async def apply_top_off(
    *,
    top_off_id=None,
    status: str | None = None,
    failure_reason: str | None = None,
    processed_at=None,
    metadata: dict | None = None,
    model=None,
    ctx=None,
    **_,
):
    """Mark a BalanceTopOff as processed and (schema-side) trigger balance crediting.

    Arguments
    ---------
    top_off_id : UUID | str | None
        Identifier of the BalanceTopOff record. If omitted, inferred from ctx.path_params.
    status : str | None
        One of TopOffStatus names (e.g. 'SUCCEEDED', 'FAILED'). Defaults to 'SUCCEEDED'.
    failure_reason : str | None
        Optional reason when marking a failed top-off.
    processed_at : datetime | None
        Optional explicit processed_at timestamp. If not provided, the schema may default.
    metadata : dict | None
        Optional metadata to merge/attach on update.
    """
    # Resolve id either from explicit arg or path params
    path_params = (ctx.get("path_params") or {}) if isinstance(ctx, dict) else {}
    tid = top_off_id or path_params.get("top_off_id") or path_params.get("id")
    if not tid:
        raise ValueError("apply_top_off requires a top_off_id (arg) or path param.")

    body = {
        "status": (status or TopOffStatus.SUCCEEDED.name),
    }
    if failure_reason:
        body["failure_reason"] = failure_reason
    if processed_at is not None:
        body["processed_at"] = processed_at
    if metadata:
        body["metadata"] = metadata

    # Set path params and payload for the model's update handler
    ctx["path_params"] = {"top_off_id": tid}
    ctx["payload"] = body
    return await model.handlers.update.handler(ctx)
