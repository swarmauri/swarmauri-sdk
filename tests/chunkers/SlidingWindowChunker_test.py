import pytest
from swarmauri.standard.chunkers.concrete.SlidingWindowChunker import SlidingWindowChunker

@pytest.mark.unit
def ubc_initialization_test():
	def test():
		chunker = SlidingWindowChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def chunk_text_test():
	def test():
		chunk_text = 'abcdefghijklmnopqsrtuvwxyz012345 '
		assert len(SlidingWindowChunker().chunk_text(chunk_text*512)) == 2
	test()


@pytest.mark.unit
def chunk_text_test_overlap():
	def test():
		assert len(SlidingWindowChunker(overlap=True, 
			step_size=21).chunk_text(chunk_text*512)) == 13
	test()


