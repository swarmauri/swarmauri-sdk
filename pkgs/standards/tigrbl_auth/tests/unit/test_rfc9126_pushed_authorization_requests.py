import pytest
from fastapi import status

from tigrbl_auth.orm.pushed_authorization_request import (
    PushedAuthorizationRequest,
    DEFAULT_PAR_EXPIRY,
)
from tigrbl_auth.deps import HTTPException
from tigrbl_auth.runtime_cfg import settings
class _Req:
    def __init__(self, form):
        self._form = form

    async def form(self):
        return self._form


@pytest.mark.unit
@pytest.mark.asyncio
async def test_par_returns_request_uri_and_expires(enable_rfc9126, db_session):
    obj = await PushedAuthorizationRequest.handlers.create.core(
        {"payload": {"params": {"client_id": "abc"}}, "db": db_session}
    )
    assert obj.request_uri.startswith("urn:ietf:params:oauth:request_uri:")
    assert obj.expires_in == DEFAULT_PAR_EXPIRY

@pytest.mark.unit
@pytest.mark.asyncio
async def test_par_disabled_returns_404():
    original = settings.enable_rfc9126
    settings.enable_rfc9126 = False
    try:
        req = _Req({})
        with pytest.raises(HTTPException) as exc:
            await PushedAuthorizationRequest._extract_form_params({"request": req})
        assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    finally:
        settings.enable_rfc9126 = original
