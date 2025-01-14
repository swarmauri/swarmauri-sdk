import os
from unittest import mock

import pytest
from swarmauri_parser_communitypdf.FitzPdfParser import PDFtoTextParser as Parser


@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == "FitzPdfParser"


@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parser():
    parser = Parser()

    file_path = "resources/demo.pdf"

    # Mock the pymupdf open method and the returned document
    with mock.patch("pymupdf.open") as mock_open:
        # Create a mock document with multiple pages
        mock_pdf_document = mock.Mock()

        # Mock pages in the document
        mock_pdf_document.__len__ = mock.Mock(return_value=2)

        # Mocking the first page's get_text method
        mock_page_1 = mock.Mock()
        mock_page_1.get_text.return_value = "This is the text from page 1.\n"

        # Mocking the second page's get_text method
        mock_page_2 = mock.Mock()
        mock_page_2.get_text.return_value = "This is the text from page 2.\n"

        # Set load_page to return the mocked pages
        mock_pdf_document.load_page.side_effect = [mock_page_1, mock_page_2]

        # Set the return value of pymupdf.open to our mock PDF document
        mock_open.return_value = mock_pdf_document

        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Check that pymupdf.open was called with the correct file path
        mock_open.assert_called_once_with(file_path)

        # Assertions
        assert len(documents) == 1, "The parser should return a list with one document."
        assert (
            documents[0].content
            == "This is the text from page 1.\nThis is the text from page 2.\n"
        ), "The extracted text content is incorrect."
        assert (
            documents[0].metadata["source"] == file_path
        ), "The metadata 'source' should match the file path."
