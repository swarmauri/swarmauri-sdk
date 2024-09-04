import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import requests
from swarmauri.community.tools.concrete.DownloadPdfTool import DownloadPdfTool as Tool

@pytest.mark.unit
def test_type():
    tool = Tool()
    assert isinstance(tool, Tool), "Component is not of the expected type."

@pytest.mark.unit
def test_resource():
    tool = Tool()
    url = "http://example.com/sample.pdf"
    destination = "sample.pdf"

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b'test data']
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tool.download_pdf(url, destination)
        assert "message" in result and result["message"] == "PDF downloaded successfully."
        assert "destination" in result and result["destination"] == destination

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    data = {"message": "PDF downloaded successfully.", "destination": "sample.pdf"}
    serialized_data = tool.serialize(data)
    deserialized_data = tool.deserialize(serialized_data)
    assert data == deserialized_data, "Serialization/Deserialization failed."

@pytest.mark.unit
def test_access():
    tool = Tool()
    assert hasattr(tool, 'download_pdf'), "Component does not have the expected access method."

@pytest.mark.unit
def test_call():
    tool = Tool()
    url = "http://example.com/sample.pdf"
    destination = "sample.pdf"

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b'test data']
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = tool.download_pdf(url, destination)
        assert result == {
            "message": "PDF downloaded successfully.",
            "destination": destination
        }, "Functionality test failed."

    with patch('requests.get', side_effect=requests.exceptions.RequestException("Error")):
        result = tool.download_pdf(url, destination)
        assert "error" in result and "Failed to download PDF" in result["error"], "Error handling test failed."

    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b'test data']
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with patch('builtins.open', side_effect=IOError("Error")):
            result = tool.download_pdf(url, destination)
            assert "error" in result and "Failed to save PDF" in result["error"], "File I/O error handling test failed."
