import pytest
from swarmauri.standard.chunkers.concrete.DelimiterBasedChunker import DelimiterBasedChunker

@pytest.mark.unit
def test_ubc_resource():
	def test():
		chunker = DelimiterBasedChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def test_chunk_text():
	def test():
		unchunked_text = 'question? test! period. run on'
		chunks = ['question?', 'test!', 'period.', 'run on']
		assert DelimiterBasedChunker().chunk_text(unchunked_text) == chunks
	test()
