import pytest
from swarmauri.standard.parsers.concrete.TextBlobNounParser import TextBlobNounParser

@pytest.mark.unit
def test_ubc_resource():
    def test():
        parser = TextBlobNounParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def test_parse():
    def test():
        documents = TextBlobNounParser().parse('One more large chapula please.')
        assert documents[0].resource == 'Document'
        assert documents[0].content == 'One more large chapula please.'
        assert documents[0].metadata['noun_phrases'] == ['large chapula']
    test()
