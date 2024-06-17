import pytest
from swarmauri.standard.chunkers.concrete.DelimiterBasedChunker import DelimiterBasedChunker

@pytest.mark.unit
def test_ubc_resource():
	def test():
		chunker = DelimiterBasedChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def chunk_text_test():
	def test():
		unchunked_text = 'test? test2! question. test'
		chunks = ['question?', 'test!', 'period.', 'run on']
		assert DelimiterBasedChunker().chunk_text(unchunked_text) == chunks
	test()
