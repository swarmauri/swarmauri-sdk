import pytest
from swarmauri.parsers.concrete.PhoneNumberExtractorParser import PhoneNumberExtractorParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == 'PhoneNumberExtractorParser'

@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse():
    document = Parser().parse('John\'s number is 555-555-5555')[0]
    assert document.content == '555-555-5555'
    assert document.resource == 'Document'
