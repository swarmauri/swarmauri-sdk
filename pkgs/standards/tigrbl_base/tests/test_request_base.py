from tigrbl_base._base._request_base import RequestBase
from tigrbl_core._spec.request_spec import RequestSpec


def test_request_base_from_scope_and_inheritance() -> None:
    scope = {
        "method": "PATCH",
        "path": "/items/1",
        "query_string": b"a=1&a=2&empty=",
        "headers": [(b"X-Test", b"yes")],
        "path_params": {"id": "1"},
        "root_path": "/api",
    }

    request = RequestBase.from_scope(scope, app="app")

    assert isinstance(request, RequestSpec)
    assert request.method == "PATCH"
    assert request.path == "/items/1"
    assert request.query == {"a": ["1", "2"], "empty": [""]}
    assert request.headers == {"x-test": "yes"}
    assert request.path_params == {"id": "1"}
    assert request.body == b""
    assert request.script_name == "/api"
    assert request.app == "app"
