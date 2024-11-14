from unittest import mock
import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri_community.parsers.concrete.PDFPlumberParser import PDFPlumberParser as Parser
from swarmauri_core.documents.IDocument import IDocument

@pytest.mark.unit
def test_parser_type():
    """
    Test to ensure the parser's type attribute is correctly set.
    """
    parser = Parser()
    assert parser.type == "PDFPlumberParser", "The type attribute should be 'PDFPlumberParser'."

@pytest.mark.unit
def test_parser_success_file_path():
    """
    Test the parser's ability to successfully parse a PDF file and extract text.
    """
    parser = Parser()
    file_path = "resources/demo.pdf"

    with mock.patch("pdfplumber.open") as mock_pdf_open:
        mock_pdf = mock.Mock()
        mock_page = mock.Mock()
        mock_page.extract_text.return_value = "Sample text from page 1."
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        documents = parser.parse(file_path)

        mock_pdf_open.assert_called_once_with(file_path)
        assert len(documents) == 1, "Parser should return a list with one document."
        assert isinstance(documents[0], IDocument), "Returned object should be an instance of IDocument."
        assert documents[0].content == "Sample text from page 1.", "Extracted content does not match expected."
        assert documents[0].metadata["page_number"] == 1, "Metadata 'page_number' should be 1."
        assert documents[0].metadata["source"] == file_path, "Metadata 'source' should match the file path."

@pytest.mark.unit
def test_parser_success_bytes():
    """
    Test the parser's ability to successfully parse PDF content from bytes.
    """
    parser = Parser()
    pdf_bytes = b"%PDF-1.4 ... (binary content)"

    with mock.patch("pdfplumber.open") as mock_pdf_open:
        mock_pdf = mock.Mock()
        mock_page = mock.Mock()
        mock_page.extract_text.return_value = "Sample text from page 1."
        mock_pdf.pages = [mock_page]
        mock_pdf_open.return_value.__enter__.return_value = mock_pdf

        documents = parser.parse(pdf_bytes)

        mock_pdf_open.assert_called_once()
        assert len(documents) == 1, "Parser should return a list with one document."
        assert isinstance(documents[0], IDocument), "Returned object should be an instance of IDocument."
        assert documents[0].content == "Sample text from page 1.", "Extracted content does not match expected."
        assert documents[0].metadata["page_number"] == 1, "Metadata 'page_number' should be 1."
        assert documents[0].metadata["source"] == "bytes", "Metadata 'source' should be 'bytes'."

@pytest.mark.unit
def test_parser_invalid_source():
    """
    Test that the parser raises a TypeError when given an invalid source type.
    """
    parser = Parser()
    invalid_source = 12345  # Not a str or bytes

    with pytest.raises(TypeError) as exc_info:
        parser.parse(invalid_source)

    assert "Source must be of type str (file path) or bytes." in str(exc_info.value), "TypeError not raised as expected."

@pytest.mark.unit
def test_parser_exception_handling():
    """
    Test the parser's exception handling when an error occurs during parsing.
    """
    parser = Parser()
    file_path = "non_existent_file.pdf"

    documents = parser.parse(file_path)

    assert len(documents) == 0, "Parser should return an empty list when an error occurs."