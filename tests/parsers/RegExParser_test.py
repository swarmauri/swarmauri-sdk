import pytest
from swarmauri.standard.parsers.concrete.RegExParser import RegExParser

@pytest.mark.unit
def test_ubc_resource():
    def test():
        # Define a pattern to match email addresses
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Create an instance of RegExParser with the email pattern
        parser = RegExParser(pattern=email_pattern)
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def test_parse():
    def test():
        # Define a pattern to match email addresses
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Create an instance of RegExParser with the email pattern
        parser = RegExParser(pattern=email_pattern)

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
    test()
