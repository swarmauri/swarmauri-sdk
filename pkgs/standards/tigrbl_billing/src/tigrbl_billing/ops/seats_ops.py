from __future__ import annotations
from typing import Optional
from tigrbl import op_ctx
from tigrbl_billing.tables.seat_allocation import SeatAllocation, SeatState

@op_ctx(alias="assign", target="custom", arity="collection", bind=SeatAllocation, persist="default")
async def seat_assign(
    *, subscription_item_id, subject_ref: str, role: Optional[str]=None, model=None, ctx=None, **_
) -> dict:
    ctx['payload'] = {
        'subscription_item_id': subscription_item_id,
        'subject_ref': subject_ref,
        'role': role,
        'state': SeatState.ACTIVE.name,
    }
    return await model.handlers.create.handler(ctx)


@op_ctx(alias="release", target="custom", arity="member", bind=SeatAllocation, persist="default")
async def seat_release(*, seat_allocation_id, model=None, ctx=None, **_) -> dict:
    ctx['path_params'] = {'seat_allocation_id': seat_allocation_id}
    ctx['payload'] = {'state': SeatState.RELEASED.name}
    return await model.handlers.update.handler(ctx)


@op_ctx(alias="suspend", target="custom", arity="member", bind=SeatAllocation, persist="default")
async def seat_suspend(*, seat_allocation_id, model=None, ctx=None, **_) -> dict:
    ctx['path_params'] = {'seat_allocation_id': seat_allocation_id}
    ctx['payload'] = {'state': SeatState.SUSPENDED.name}
    return await model.handlers.update.handler(ctx)
