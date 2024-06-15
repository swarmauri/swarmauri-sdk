import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.concrete.URLExtractorParser import URLExtractorParser

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        parser = URLExtractorParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def parser_test():
    def test():
        documents = URLExtractorParser().parse('https://www.swarmauri.com, swarmauri.app, and swarmauri agents.')
        assert len(documents) == 1
        assert documents[0].resource == 'Document'
        assert documents[0].content == 'https://www.swarmauri.com'
        assert documents[0].metadata['source'] == 'URLExtractor'
    test()
