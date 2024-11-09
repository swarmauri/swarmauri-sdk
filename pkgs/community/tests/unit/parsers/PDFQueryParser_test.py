import pytest
from unittest import mock
from swarmauri.documents.concrete.Document import Document
from  swarmauri_community.parsers.concrete.PDFQueryParser import PDFQueryParser as Parser
from swarmauri_core.documents.IDocument import IDocument

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
    assert parser.type == "PDFQueryParser", "The type attribute should be 'PDFQueryParser'."

@pytest.mark.unit
def test_parser_serialization():
    """
    Test to ensure the parser can be serialized and deserialized correctly.
    """
    parser = Parser()
    serialized = parser.model_dump_json()
    deserialized = Parser.model_validate_json(serialized)
    assert parser.id == deserialized.id, "Serialization and deserialization should preserve the parser's ID."

@pytest.mark.unit
def test_parser_success_file_path():
    """
    Test the parser's ability to successfully parse a PDF file and extract text from file path.
    """
    parser = Parser()
    file_path = "resources/demo.pdf"

    # Mock the PDFQuery and its load method
    with mock.patch("pdfquery.PDFQuery") as mock_pdfquery:
        mock_pdf_instance = mock_pdfquery.return_value
        mock_pdf_instance.tree.text_content.return_value = "Sample text from PDF."

        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Assertions
        mock_pdfquery.assert_called_once_with(file_path)
        mock_pdf_instance.load.assert_called_once()
        assert len(documents) == 1, "Parser should return a list with one document."
        assert isinstance(documents[0], IDocument), "Returned object should be an instance of IDocument."
        assert documents[0].content == "Sample text from PDF.", "Extracted content does not match expected."
        assert documents[0].metadata["source"] == file_path, "Metadata 'source' should match the file path."

@pytest.mark.unit
def test_parser_success_bytes():
    """
    Test the parser's ability to successfully parse PDF content from bytes.
    """
    parser = Parser()
    pdf_bytes = b"%PDF-1.4 ... (binary content)"

    # Mock the PDFQuery and its load method
    with mock.patch("pdfquery.PDFQuery") as mock_pdfquery:
        mock_pdf_instance = mock_pdfquery.return_value
        mock_pdf_instance.tree.text_content.return_value = "Sample text from PDF."

        # Call the parser's parse method
        documents = parser.parse(pdf_bytes)

        # Assertions
        mock_pdfquery.assert_called_once()
        assert len(documents) == 1, "Parser should return a list with one document."
        assert isinstance(documents[0], IDocument), "Returned object should be an instance of IDocument."
        assert documents[0].content == "Sample text from PDF.", "Extracted content does not match expected."
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

    # Mock an exception during the PDF loading
    with mock.patch("pdfquery.PDFQuery", side_effect=Exception("File not found")):
        documents = parser.parse(file_path)

    # Assertions
    assert len(documents) == 0, "Parser should return an empty list when an error occurs."