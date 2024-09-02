import pytest
from swarmauri.standard.tools.concrete.RequestsTool import RequestsTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'RequestsTool'

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
    try:
        response = tool(method, url, **kwargs)

        assert response.status_code == 200

        assert 'url' in response.json()

    except Exception as e:
        pytest.fail(f"{method.upper()} request failed with error: {e}")