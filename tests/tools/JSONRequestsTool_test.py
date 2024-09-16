import pytest
from swarmauri.standard.tools.concrete.JSONRequestsTool import JSONRequestsTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'JSONRequestsTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize("method, url, kwargs", [
    ('get', 'https://httpbin.org/get', {}),
    ('post', 'https://httpbin.org/post', {'json': {'key': 'value'}}),
    ('put', 'https://httpbin.org/put', {'json': {'key': 'value'}}),
    ('delete', 'https://httpbin.org/delete', {}),
])

@pytest.mark.unit
def test_call(method, url, kwargs):
    tool = Tool()

    expected_keys = {"response_content", "response_status"}

    try:
        result = tool(method, url, **kwargs)

        assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
        assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"

        assert result.get(
            "response_status") == 200, f"Expected Reading Ease value is {200}, but got {result.get('response_status')}"
    except Exception as e:
        pytest.fail(f"{method.upper()} request failed with error: {e}")