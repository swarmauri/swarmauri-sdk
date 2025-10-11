from __future__ import annotations
from tigrbl import op_ctx
from tigrbl_billing.tables.credit_grant import CreditGrant, GrantStatus

@op_ctx(alias="apply_grant", target="custom", arity="member", bind=CreditGrant, persist="default")
async def apply_grant(*, grant_id, model=None, ctx=None, **_):
    ctx['path_params'] = {'grant_id': grant_id}
    ctx['payload'] = {'status': GrantStatus.ACTIVE.name}
    return await model.handlers.update.handler(ctx)

@op_ctx(alias="revoke_grant", target="custom", arity="member", bind=CreditGrant, persist="default")
async def revoke_grant(*, grant_id, amount: int | None=None, reason: str | None=None, model=None, ctx=None, **_):
    ctx['path_params'] = {'grant_id': grant_id}
    body = {'status': GrantStatus.REVOKED.name}
    if amount is not None:
        body['revoke_amount'] = int(amount)
    if reason:
        body['revoke_reason'] = reason
    ctx['payload'] = body
    return await model.handlers.update.handler(ctx)
