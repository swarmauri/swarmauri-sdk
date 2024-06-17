import pytest
from swarmauri.standard.chunkers.concrete.FixedLengthChunker import FixedLengthChunker

@pytest.mark.unit
def test_ubc_resource():
	def test():
		chunker = FixedLengthChunker()
		assert chunker.resource == 'Chunker'
	test()

@pytest.mark.unit
def chunk_text_test():
	def test():
		assert len(FixedLengthChunker().chunk_text('ab '*512)) == 6
	test()
