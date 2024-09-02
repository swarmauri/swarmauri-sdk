import pytest
from swarmauri.standard.parsers.concrete.BeautifulSoupElementParser import BeautifulSoupElementParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    assert Parser().type == 'BeautifulSoupElementParser'


@pytest.mark.unit
def test_initialization():
    parser = Parser()
    assert type(parser.id) == str

@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id

@pytest.mark.unit
def test_call():
    parser = Parser()
    input_text = "dummy text"
    assert parser(input_text) == "dummy text"
