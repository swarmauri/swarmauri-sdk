import httpx
import pytest

from tigrbl_client._crud import CRUDMixin


class DummyClient(CRUDMixin):
    pass


def test_process_response_422_includes_detail():
    client = DummyClient()
    request = httpx.Request("POST", "http://example.com/services")
    response = httpx.Response(
        422,
        json={"detail": [{"loc": ["body", "tenant_id"], "msg": "Field required"}]},
        request=request,
    )
    with pytest.raises(httpx.HTTPStatusError) as exc:
        client._process_response(response)
    assert "Field required" in str(exc.value)
