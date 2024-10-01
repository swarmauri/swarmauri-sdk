import pytest
from swarmauri.chunkers.concrete.FixedLengthChunker import FixedLengthChunker

@pytest.mark.unit
def test_ubc_resource():	
	chunker = FixedLengthChunker()
	assert chunker.resource == 'Chunker'

@pytest.mark.unit
def test_ubc_type():
	chunker = FixedLengthChunker()
	assert chunker.type == 'FixedLengthChunker'

@pytest.mark.unit
def test_chunk_text():
	assert len(FixedLengthChunker().chunk_text('ab '*512)) == 6

@pytest.mark.unit
def test_serialization():
	chunker = FixedLengthChunker()
	assert chunker.id == FixedLengthChunker.model_validate_json(chunker.model_dump_json()).id