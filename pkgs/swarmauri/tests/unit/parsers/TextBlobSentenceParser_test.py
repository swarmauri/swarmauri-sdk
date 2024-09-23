import pytest
from swarmauri.parsers.concrete.TextBlobSentenceParser import TextBlobSentenceParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == 'TextBlobSentenceParser'

@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id

@pytest.mark.unit
def test_parse():
    documents = Parser().parse('One more large chapula please.')
    assert documents[0].resource == 'Document'
    assert documents[0].content == 'One more large chapula please.'
