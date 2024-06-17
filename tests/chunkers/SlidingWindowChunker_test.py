import pytest
from swarmauri.standard.chunkers.concrete.SlidingWindowChunker import SlidingWindowChunker

@pytest.mark.unit
def test_ubc_resource():
	def test():
		chunker = SlidingWindowChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def test_chunk_text():
	def test():
		unchunked_text = 'abcdefghijklmnopqsrtuvwxyz012345 '
		assert len(SlidingWindowChunker().chunk_text(unchunked_text*512)) == 2
	test()


@pytest.mark.unit
def test_chunk_text_overlap():
	def test():
		unchunked_text = 'abcdefghijklmnopqsrtuvwxyz012345 '
		assert len(SlidingWindowChunker(overlap=True, 
			step_size=21).chunk_text(unchunked_text*512)) == 13
	test()


