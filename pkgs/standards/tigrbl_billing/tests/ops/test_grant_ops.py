import pytest

from tigrbl_billing.ops import grant_ops
from tigrbl_billing.tables.credit_grant import GrantStatus


@pytest.mark.asyncio
async def test_apply_grant_marks_active(recording_model):
    ctx = {}

    result = await grant_ops.apply_grant(
        grant_id="gr_1", model=recording_model, ctx=ctx
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"grant_id": "gr_1"}
    assert call_ctx["payload"] == {"status": GrantStatus.ACTIVE.name}


@pytest.mark.asyncio
async def test_revoke_grant_includes_optional_fields(recording_model):
    ctx = {}

    result = await grant_ops.revoke_grant(
        grant_id="gr_2",
        amount="25",
        reason="expired",
        model=recording_model,
        ctx=ctx,
    )

    assert result == {"status": "ok"}
    call_ctx = recording_model.handlers.update.calls[0]
    assert call_ctx["path_params"] == {"grant_id": "gr_2"}
    assert call_ctx["payload"] == {
        "status": GrantStatus.REVOKED.name,
        "revoke_amount": 25,
        "revoke_reason": "expired",
    }
