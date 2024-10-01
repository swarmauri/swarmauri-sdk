import pytest
from swarmauri.parsers.concrete.RegExParser import RegExParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    # Define a pattern to match email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # Create an instance of RegExParser with the email pattern
    parser = Parser(pattern=email_pattern)
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # Create an instance of RegExParser with the email pattern
    parser = Parser(pattern=email_pattern)
    assert parser.type == 'RegExParser'

@pytest.mark.unit
def test_serialization():
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # Create an instance of RegExParser with the email pattern
    parser = Parser(pattern=email_pattern)
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id

@pytest.mark.unit
def test_parse():
    # Define a pattern to match email addresses
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    # Create an instance of RegExParser with the email pattern
    parser = Parser(pattern=email_pattern)

    # Example text to parse
    text = """
    Here are some email addresses:
    alice@example.com
    bob.smith@work-email.org
    contact@company.co.uk
    """
    # Parse the text
    documents = parser.parse(text)

    assert documents[0].content == 'alice@example.com'
    assert documents[1].content == 'bob.smith@work-email.org'
    assert documents[2].content == 'contact@company.co.uk'
    assert documents[0].resource == 'Document'
