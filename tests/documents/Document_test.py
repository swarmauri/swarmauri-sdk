import pytest
from swarmauri.standard.documents.concrete.Document import Document

@pytest.mark.unit
def ubc_initialization_test():
	def test():
		document = Document(content="test")
		assert document.resource == 'Document'
	test()

@pytest.mark.unit
def content_test():
	def test():
		document = Document(content="test")
		assert document.content == 'test'
	test()