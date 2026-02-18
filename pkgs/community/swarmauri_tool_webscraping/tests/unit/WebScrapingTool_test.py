import pytest
import requests
from swarmauri_tool_webscraping.WebScrapingTool import (
    WebScrapingTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "WebScrapingTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "url, selector, expected_substring",
    [
        ("https://example.com", "h1", "Example Domain"),  # Valid page, valid selector
        (
            "https://example.com",
            "p",
            "illustrative",
        ),  # Valid page, another valid selector
        (
            "https://example.com/nonexistent",
            "h1",
            "404",
        ),  # Invalid page, expect part of the error
        (
            "https://example.com",
            ".nonexistent-class",
            "",
        ),  # Valid page, invalid selector
    ],
)
@pytest.mark.unit
def test_call(url, selector, expected_substring):
    """
    Test Tool's ability to extract text from a webpage or handle errors.

    Args:
        url (str): The URL of the webpage to extract content from.
        selector (str): The CSS selector to extract specific content.
        expected_substring (str): The expected substring within the extracted text or error message.

    The test validates:
    - If the response is a dictionary.
    - Whether "extracted_text" or "error" is in the dictionary.
    - If extraction is successful, check that the text contains the expected substring.
    - If an error occurs, ensure the error contains the expected message.
    """

    class MockResponse:
        def __init__(self, content, status_code=200):
            self.content = content.encode("utf-8")
            self.status_code = status_code

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"{self.status_code} Client Error")

    def mock_get(mock_url):
        if mock_url == "https://example.com":
            return MockResponse(
                (
                    "<html><body><h1>Example Domain</h1>"
                    "<p>This domain is for use in illustrative examples.</p>"
                    "</body></html>"
                ),
                200,
            )
        if mock_url == "https://example.com/nonexistent":
            return MockResponse(
                "<html><body><h1>404 Not Found</h1></body></html>",
                404,
            )
        raise requests.RequestException("Unexpected URL")

    tool = Tool()
    original_get = requests.get
    requests.get = mock_get
    try:
        result = tool(url, selector)
    finally:
        requests.get = original_get

    # Check the result type
    assert isinstance(result, dict), "Result should be a dictionary."

    # Check if the result contains either 'extracted_text' or 'error'
    assert "extracted_text" in result or "error" in result, (
        "Result should contain either 'extracted_text' or 'error'."
    )

    # Handle the result depending on whether extraction was successful
    if "extracted_text" in result:
        assert expected_substring in result["extracted_text"], (
            f"Expected '{expected_substring}' in extracted text."
        )
    else:
        assert expected_substring in result["error"], (
            f"Expected '{expected_substring}' in error message. Actual error: {result['error']}"
        )
