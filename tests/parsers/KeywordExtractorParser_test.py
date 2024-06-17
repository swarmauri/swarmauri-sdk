import pytest
from swarmauri.standard.parsers.concrete.KeywordExtractorParser import KeywordExtractorParser

@pytest.mark.unit
def test_ubc_resource():
	def test():
		parser = KeywordExtractorParser()
		assert parser.resource == 'Parser'
	test()

@pytest.mark.unit
def test_parse():
	def test():
		assert KeywordExtractorParser().parse('test two burgers')[2].resource == 'Document'
		assert KeywordExtractorParser().parse('test two burgers')[2].content == 'burgers'
	test()
