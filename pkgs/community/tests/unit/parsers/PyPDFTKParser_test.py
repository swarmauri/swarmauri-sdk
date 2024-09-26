import pytest
from unittest import mock
from swarmauri_community.parsers.concrete.PyPDFTKParser import PyPDFTKParser as Parser
from swarmauri_core.documents.IDocument import IDocument
from swarmauri.documents.concrete.Document import Document

PyPDFTKError = Exception  

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
    assert parser.type == "PyPDFTKParser", "The type attribute should be 'PyPDFTKParser'."


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
def test_parser_success():
    """
    Test the parser's ability to successfully parse a PDF and extract data fields.
    """
    parser = Parser()
    file_path = "resources/demo.pdf"

    # Mock the pypdftk.dump_data_fields method
    with mock.patch("pypdftk.dump_data_fields") as mock_dump_data_fields:
        # Define the mock return value
        mock_dump_data_fields.return_value = {
            'Field1': 'Value1',
            'Field2': 'Value2'
        }

        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Assertions
        mock_dump_data_fields.assert_called_once_with(file_path)
        assert len(documents) == 1, "Parser should return a list with one document."
        assert isinstance(documents[0], IDocument), "Returned object should be an instance of IDocument."
        expected_content = "Field1: Value1\nField2: Value2"
        assert documents[0].content == expected_content, "Extracted content does not match expected."
        assert documents[0].metadata["source"] == file_path, "Metadata 'source' should match the file path."


@pytest.mark.unit
def test_parser_no_fields():
    """
    Test the parser's behavior when no data fields are found in the PDF.
    """
    parser = Parser()
    file_path = "resources/empty_fields.pdf"

    # Mock the pypdftk.dump_data_fields method to return an empty dictionary
    with mock.patch("pypdftk.dump_data_fields", return_value={}) as mock_dump_data_fields:
        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Assertions
        mock_dump_data_fields.assert_called_once_with(file_path)
        assert len(documents) == 0, "Parser should return an empty list when no fields are found."


@pytest.mark.unit
def test_parser_pypdftk_error():
    """
    Test the parser's behavior when pypdftk raises an exception.
    """
    parser = Parser()
    file_path = "resources/error.pdf"

    # Mock the pypdftk.dump_data_fields method to raise an Exception
    with mock.patch("pypdftk.dump_data_fields", side_effect=PyPDFTKError("Failed to parse PDF fields")) as mock_dump_data_fields:
        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Assertions
        mock_dump_data_fields.assert_called_once_with(file_path)
        assert len(documents) == 0, "Parser should return an empty list when an exception occurs."


@pytest.mark.unit
def test_parser_file_not_found():
    """
    Test the parser's behavior when the specified PDF file does not exist.
    """
    parser = Parser()
    file_path = "resources/non_existent.pdf"

    # Mock the pypdftk.dump_data_fields method to raise FileNotFoundError
    with mock.patch("pypdftk.dump_data_fields", side_effect=FileNotFoundError("File not found")) as mock_dump_data_fields:
        # Call the parser's parse method
        documents = parser.parse(file_path)

        # Assertions
        mock_dump_data_fields.assert_called_once_with(file_path)
        assert len(documents) == 0, "Parser should return an empty list when the file is not found."


@pytest.mark.unit
def test_parser_invalid_input_type():
    """
    Test the parser's behavior when an invalid input type is provided.
    """
    parser = Parser()
    invalid_input = 123  # Non-string input

    # Expecting a ValueError when input is not a string
    with pytest.raises(ValueError, match="PyPDFTKParser expects a file path as a string."):
        parser.parse(invalid_input)
