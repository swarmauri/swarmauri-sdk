from unittest import mock

import pytest
from swarmauri_parser_pypdf2.PyPDF2Parser import PyPDF2Parser as Parser
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
    assert parser.type == "PyPDF2Parser", "The type attribute should be 'PyPDF2Parser'."


@pytest.mark.unit
def test_parser_serialization():
    """
    Test to ensure the parser can be serialized and deserialized correctly.
    """
    parser = Parser()
    serialized = parser.model_dump_json()
    deserialized = Parser.model_validate_json(serialized)
    assert parser.id == deserialized.id, (
        "Serialization and deserialization should preserve the parser's ID."
    )


@pytest.mark.unit
def test_parser_success_file_path():
    """
    Test the parser's ability to successfully parse a PDF file and extract text.
    """
    parser = Parser()
    file_path = "resources/demo.pdf"

    # Mock the open function and PyPDF2.PdfReader
    with mock.patch(
        "builtins.open", mock.mock_open(read_data=b"PDF file content")
    ) as mock_file:
        with mock.patch("PyPDF2.PdfReader") as mock_pdf_reader:
            # Mock reader.pages
            mock_page = mock.Mock()
            mock_page.extract_text.return_value = "Sample text from page 1."
            mock_pdf_reader.return_value.pages = [mock_page]

            # Call the parser's parse method
            documents = parser.parse(file_path)

            # Assertions
            mock_file.assert_called_once_with(file_path, "rb")
            mock_pdf_reader.assert_called_once()
            assert len(documents) == 1, "Parser should return a list with one document."
            assert isinstance(documents[0], IDocument), (
                "Returned object should be an instance of IDocument."
            )
            assert documents[0].content == "Sample text from page 1.", (
                "Extracted content does not match expected."
            )
            assert documents[0].metadata["page_number"] == 1, (
                "Metadata 'page_number' should be 1."
            )
            assert documents[0].metadata["source"] == file_path, (
                "Metadata 'source' should match the file path."
            )


@pytest.mark.unit
def test_parser_success_bytes():
    """
    Test the parser's ability to successfully parse PDF content from bytes.
    """
    parser = Parser()
    pdf_bytes = b"%PDF-1.4 ... (binary content)"

    # Mock the PyPDF2.PdfReader and its methods
    with mock.patch("PyPDF2.PdfReader") as mock_pdf_reader:
        # Mock reader.pages
        mock_page = mock.Mock()
        mock_page.extract_text.return_value = "Sample text from page 1."
        mock_pdf_reader.return_value.pages = [mock_page]

        # Call the parser's parse method
        documents = parser.parse(pdf_bytes)

        # Assertions
        mock_pdf_reader.assert_called_once()
        assert len(documents) == 1, "Parser should return a list with one document."
        assert isinstance(documents[0], IDocument), (
            "Returned object should be an instance of IDocument."
        )
        assert documents[0].content == "Sample text from page 1.", (
            "Extracted content does not match expected."
        )
        assert documents[0].metadata["page_number"] == 1, (
            "Metadata 'page_number' should be 1."
        )
        assert documents[0].metadata["source"] == "bytes", (
            "Metadata 'source' should be 'bytes'."
        )


@pytest.mark.unit
def test_parser_invalid_source():
    """
    Test that the parser raises a TypeError when given an invalid source type.
    """
    parser = Parser()
    invalid_source = 12345  # Not a str or bytes

    with pytest.raises(TypeError) as exc_info:
        parser.parse(invalid_source)

    assert "Source must be of type str (file path) or bytes." in str(exc_info.value), (
        "TypeError not raised as expected."
    )


@pytest.mark.unit
def test_parser_exception_handling():
    """
    Test the parser's exception handling when an error occurs during parsing.
    """
    parser = Parser()
    file_path = "non_existent_file.pdf"

    # Call the parser's parse method with a non-existent file
    documents = parser.parse(file_path)

    # Assertions
    assert len(documents) == 0, (
        "Parser should return an empty list when an error occurs."
    )
