import pytest
from swarmauri.standard.parsers.concrete.XMLParser import XMLParser

@pytest.mark.unit
def test_ubc_resource():
    def test():
        parser = XMLParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def test_parse():
    def test():
        documents = XMLParser(element_tag='project').parse('<root><project>stuff inside project</project><project>test</project></root>')
        assert len(documents) == 1
        assert documents[0].resource == 'Document'
        assert documents[0].content == 'stuff inside project'
        assert documents[1].resource == 'Document'
        assert documents[1].content == 'test'
    test()
