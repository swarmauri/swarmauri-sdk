import pytest
from swarmauri.standard.chunkers.concrete.FixedLengthChunker import FixedLengthChunker

@pytest.mark.unit
def ubc_initialization_test():
	def test():
		chunker = FixedLengthChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def chunk_text_test():
	def test():
		assert len(FixedLengthChunker().chunk_text('ab '*512)) == 6
	test()
