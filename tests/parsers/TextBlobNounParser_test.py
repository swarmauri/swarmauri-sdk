import pytest
from swarmauri.standard.parsers.concrete.TextBlobNounParser import TextBlobNounParser

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        parser = TextBlobNounParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def parser_test():
    def test():
        documents = TextBlobNounParser().parse('One more large chapula please.')
        assert documents[0].resource == 'Document'
        assert documents[0].content == 'One more large chapula please.'
        assert documents[0].metadata['noun_phrases'] == ['large chapula']
    test()
