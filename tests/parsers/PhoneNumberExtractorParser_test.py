import pytest
from swarmauri.standard.parsers.concrete.PhoneNumberExtractorParser import PhoneNumberExtractorParser

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        parser = PhoneNumberExtractorParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def parser_test():
    def test():
        document = PhoneNumberExtractorParser().parse('John\'s number is 555-555-5555')[0]
        assert document.content == '555-555-5555'
        assert document.resource == 'Document'
    test()
