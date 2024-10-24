import pytest
from swarmauri.tools.concrete import JSONRequestsTool as Tool


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
    assert type(tool.id) == str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "method, url, kwargs",
    [
        ("get", "https://httpbin.org/get", {}),
        ("post", "https://httpbin.org/post", {"json": {"key": "value"}}),
        ("put", "https://httpbin.org/put", {"json": {"key": "value"}}),
        ("delete", "https://httpbin.org/delete", {}),
    ],
)
@pytest.mark.unit
def test_call(method, url, kwargs):
    tool = Tool()

    expected_keys = {"args", "headers", "origin", "url"}

    try:
        result = tool(method, url, **kwargs)

        assert isinstance(
            result, dict
        ), f"Expected dict, but got {type(result).__name__}"
        assert expected_keys.issubset(
            result.keys()
        ), f"Expected keys {expected_keys} to be a subset of {result.keys()}"

        # Check for method-specific keys
        if method in ["post", "put", "delete"]:
            assert "json" in result, f"Expected 'json' key for {method.upper()} method"
            if kwargs.get("json"):
                assert (
                    result["json"] == kwargs["json"]
                ), f"Expected JSON payload {kwargs['json']}, but got {result['json']}"

        assert result["url"] == url, f"Expected URL {url}, but got {result['url']}"

    except Exception as e:
        pytest.fail(f"{method.upper()} request failed with error: {e}")
