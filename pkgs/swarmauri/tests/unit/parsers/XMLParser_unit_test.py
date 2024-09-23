import pytest
from swarmauri.parsers.concrete.XMLParser import XMLParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == 'XMLParser'

@pytest.mark.unit
def test_serialization():
    element_tag = 'test'
    parser = Parser(element_tag=element_tag)
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id
    assert parser.element_tag == element_tag

@pytest.mark.unit
def test_parse():
    documents = Parser(element_tag='project').parse('<root><project>stuff inside project</project><project>test</project></root>')
    assert len(documents) == 2
    assert documents[0].resource == 'Document'
    assert documents[0].content == 'stuff inside project'
    assert documents[1].resource == 'Document'
    assert documents[1].content == 'test'
