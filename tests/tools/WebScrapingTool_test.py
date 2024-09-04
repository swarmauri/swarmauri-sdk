import pytest
from swarmauri.standard.tools.concrete.WebScrapingTool import WebScrapingTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'WebScrapingTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize("url, selector, expected_substring", [
    ("https://example.com", "h1", "Example Domain"),
    ("https://example.com", "p", "illustrative"),
    ("https://example.com/nonexistent", "h1", "Request Exception"),
    ("https://example.com", ".nonexistent-class", ""),
])
@pytest.mark.unit
def test_call(url, selector, expected_substring):
    tool = Tool()
    result = tool(url, selector)
    assert expected_substring in result
