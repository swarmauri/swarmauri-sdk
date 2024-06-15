import pytest
from swarmauri.standard.documents.concrete.Document import Document
from swarmauri.standard.parsers.concrete.HTMLTagStripParser import HTMLTagStripParser

@pytest.mark.unit
def ubc_initialization_test():
	def test():
		parser = HTMLTagStripParser()
		assert parser.resource == 'Parser'
	test()

@pytest.mark.unit
def parser_test():
	def test():
		assert HTMLTagStripParser().parse('<html>test</html>')[0].resource == 'Document'
		assert HTMLTagStripParser().parse('<html>test</html>')[0].content == 'test'
	test()
