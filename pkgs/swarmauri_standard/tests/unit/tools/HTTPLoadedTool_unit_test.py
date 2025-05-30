import pytest
from unittest.mock import patch, MagicMock

from swarmauri_standard.tools.HTTPLoadedTool import HTTPLoadedTool as Tool


@pytest.mark.unit
@patch("httpx.get")
def test_ubc_resource(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "components: []"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    tool = Tool(url="http://example.com/manifest.yaml")
    assert tool.resource == "Tool"
    mock_get.assert_called_once_with("http://example.com/manifest.yaml", headers=None)


@pytest.mark.unit
@patch("httpx.get")
def test_ubc_type(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "components: []"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    assert Tool(url="http://example.com/manifest.yaml").type == "HTTPLoadedTool"
    mock_get.assert_called_once()


@pytest.mark.unit
@patch("httpx.get")
def test_initialization(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "components: []"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    tool = Tool(url="http://example.com/manifest.yaml")
    assert isinstance(tool.id, str)
    mock_get.assert_called_once()


@pytest.mark.unit
@patch("httpx.get")
def test_serialization(mock_get):
    mock_resp = MagicMock()
    mock_resp.text = "components: []"
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    tool = Tool(url="http://example.com/manifest.yaml")
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id
    mock_get.assert_called_once()


@pytest.mark.unit
@patch("httpx.get")
def test_call(mock_get):
    manifest = """
components:
  - type: CalculatorTool
"""
    mock_resp = MagicMock()
    mock_resp.text = manifest
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    tool = Tool(url="http://example.com/manifest.yaml")
    result = tool()

    assert len(result) == 1
    assert result[0].type == "CalculatorTool"
    mock_get.assert_called_once_with("http://example.com/manifest.yaml", headers=None)


@pytest.mark.unit
@patch("httpx.get")
def test_manifest_metadata(mock_get):
    manifest = """
name: Custom
description: Example description
parameters:
  - name: foo
    description: bar
    input_type: string
components: []
"""
    mock_resp = MagicMock()
    mock_resp.text = manifest
    mock_resp.raise_for_status = MagicMock()
    mock_get.return_value = mock_resp

    tool = Tool(url="http://example.com/manifest.yaml")

    assert tool.name == "Custom"
    assert tool.description == "Example description"
    assert len(tool.parameters) == 1
    mock_get.assert_called_once_with("http://example.com/manifest.yaml", headers=None)

