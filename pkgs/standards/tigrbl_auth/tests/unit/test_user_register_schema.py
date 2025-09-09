import pytest
from autoapi.v3.bindings import bind
from tigrbl_auth.orm import User
from tigrbl_auth.routers.schemas import RegisterIn, TokenPair


@pytest.mark.unit
def test_register_op_has_request_and_response_schema():
    bind(User)
    assert issubclass(User.schemas.register.in_, RegisterIn)
    assert issubclass(User.schemas.register.out, TokenPair)
