import pytest
from swarmauri.standard.chunkers.concrete.SentenceChunker import SentenceChunker

@pytest.mark.unit
def test_ubc_resource():
	def test():
		chunker = SentenceChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def test_chunk_text():
	def test():
		unchunked_text = 'A walk in the park is a nice start. After the walk, let us talk.'
		chunks = ['A walk in the park is a nice start.', 'After the walk, let us talk.']
		assert SentenceChunker().chunk_text(unchunked_text) == chunks
	test()
