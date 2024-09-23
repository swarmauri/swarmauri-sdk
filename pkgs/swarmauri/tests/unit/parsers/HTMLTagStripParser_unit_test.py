import pytest
from swarmauri.parsers.concrete.HTMLTagStripParser import HTMLTagStripParser as Parser

@pytest.mark.unit
def test_ubc_resource():
	parser = Parser()
	assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == 'HTMLTagStripParser'

@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id

@pytest.mark.unit
def test_parse():
	assert Parser().parse('<html>test</html>')[0].resource == 'Document'
	assert Parser().parse('<html>test</html>')[0].content == 'test'
