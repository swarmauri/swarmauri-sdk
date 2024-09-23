import base64
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import requests
from swarmauri_community.tools.concrete.DownloadPdfTool import DownloadPDFTool as Tool


@pytest.mark.unit
def test_type():
    tool = Tool()
    assert isinstance(tool, Tool), "Component is not of the expected type."


@pytest.mark.unit
def test_resource():
    tool = Tool()
    url = "http://example.com/sample.pdf"

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tool(url)  # Calling the tool directly
        assert (
            "message" in result
            and "PDF downloaded and encoded successfully." in result["message"]
        )


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_access():
    tool = Tool()
    assert callable(tool), "Component is not callable as expected."


@pytest.mark.unit
def test_call():
    tool = Tool()
    url = "http://example.com/sample.pdf"

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tool(url)
        encoded_pdf = base64.b64encode(b"test data").decode("utf-8")

        assert isinstance(result, dict), "Result is not a dictionary."
        assert result == {
            "message": "PDF downloaded and encoded successfully.",
            "content": encoded_pdf,
        }, "Functionality test failed."

    with patch(
        "requests.get", side_effect=requests.exceptions.RequestException("Error")
    ):
        result = tool(url)
        assert (
            "message" in result and "content" in result
        ) or "error" in result, "Error handling test failed."

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b"test data"]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Test network request failure handling
        with patch(
            "requests.get", side_effect=requests.exceptions.RequestException("Error")
        ):
            result = tool(url)
            assert (
                "error" in result and "Failed to download PDF" in result["error"]
            ), "Error handling test failed."
