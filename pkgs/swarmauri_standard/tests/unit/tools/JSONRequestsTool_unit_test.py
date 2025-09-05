import json
import httpx
import pytest

from swarmauri_standard.tools.JSONRequestsTool import JSONRequestsTool as Tool


def _mock_httpbin(request: httpx.Request) -> httpx.Response:
    data = {
        "args": dict(request.url.params),
        "headers": dict(request.headers),
        "origin": "0.0.0.0",
        "url": str(request.url),
    }
    if request.method in {"POST", "PUT", "DELETE"}:
        if request.content:
            try:
                data["json"] = json.loads(request.content.decode())
            except json.JSONDecodeError:
                data["json"] = None
        else:
            data["json"] = None
    return httpx.Response(200, json=data)


@pytest.fixture
def tool():
    transport = httpx.MockTransport(_mock_httpbin)
    client = httpx.Client(transport=transport)
    return Tool(client=client)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "JSONRequestsTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "https://example.com/get", {}),
        ("post", "https://example.com/post", {"json": {"key": "value"}}),
        ("put", "https://example.com/put", {"json": {"key": "value"}}),
        ("delete", "https://example.com/delete", {}),
    ],
)
@pytest.mark.unit
def test_call(method, url, kwargs, tool):
    expected_keys = {"args", "headers", "origin", "url"}

    result = tool(method, url, **kwargs)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), (
        f"Expected keys {expected_keys} to be a subset of {result.keys()}"
    )

    if method in ["post", "put", "delete"]:
        assert "json" in result, f"Expected 'json' key for {method.upper()} method"
        if kwargs.get("json"):
            assert result["json"] == kwargs["json"], (
                f"Expected JSON payload {kwargs['json']}, but got {result['json']}"
            )

    assert result["url"] == url, f"Expected URL {url}, but got {result['url']}"
