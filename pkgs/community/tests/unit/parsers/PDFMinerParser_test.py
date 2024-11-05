from unittest import mock

import pytest
from swarmauri_community.parsers.concrete.PDFMinerParser import PDFMinerParser as Parser


@pytest.mark.unit
def test_parser_resource():
    """
    Test to ensure the parser's resource attribute is correctly set.
    """
    parser = Parser()
    assert parser.resource == "Parser", "The resource attribute should be 'Parser'."


@pytest.mark.unit
def test_parser_type():
    """
    Test to ensure the parser's type attribute is correctly set.
    """
    parser = Parser()
    assert parser.type == "PDFMinerParser", "The type attribute should be 'PDFMinerParser'."


@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parser_success_file_path():
    """
    Test the parser's ability to successfully parse a PDF file and extract text.
    """
    parser = Parser()

    file_path = "resources/demo.pdf"

    # Mock the extract_text function
    # TODO: Mocking the extract_text directly from pdfminer.high_level.extract_text did not work
    with mock.patch("swarmauri_community.parsers.concrete.PDFMinerParser.extract_text") as mock_extract_text:
        # Mock page content
        mock_extract_text.return_value = "Sample text from page 1."

        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Assertions
        mock_extract_text.assert_called_once_with(file_path)
        assert len(documents) == 1, "Parser should return a list with one document."
        assert documents[0].content == "Sample text from page 1.", "Extracted content does not match expected."
        assert documents[0].metadata["source"] == file_path, "Metadata 'source' should match the file path."