import pytest

from tigrbl import Router


@pytest.mark.unit
def test_router_exposes_no_call_handler_shim() -> None:
    router = Router()
    assert not hasattr(router, "call_handler")
