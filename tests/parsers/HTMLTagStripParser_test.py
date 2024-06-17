import pytest
from swarmauri.standard.parsers.concrete.HTMLTagStripParser import HTMLTagStripParser

@pytest.mark.unit
def test_ubc_resource():
	def test():
		parser = HTMLTagStripParser()
		assert parser.resource == 'Parser'
	test()

@pytest.mark.unit
def test_parse():
	def test():
		assert HTMLTagStripParser().parse('<html>test</html>')[0].resource == 'Document'
		assert HTMLTagStripParser().parse('<html>test</html>')[0].content == 'test'
	test()
