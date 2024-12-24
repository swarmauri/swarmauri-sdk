import pytest
from swarmauri.chunkers.concrete.SlidingWindowChunker import SlidingWindowChunker

@pytest.mark.unit
def test_ubc_resource():
	chunker = SlidingWindowChunker()
	assert chunker.resource == 'Chunker'

@pytest.mark.unit
def test_ubc_type():
	chunker = SlidingWindowChunker()
	assert chunker.type == 'SlidingWindowChunker'

@pytest.mark.unit
def test_chunk_text():
	unchunked_text = 'abcdefghijklmnopqsrtuvwxyz012345 '
	assert len(SlidingWindowChunker().chunk_text(unchunked_text*512)) == 2

@pytest.mark.unit
def test_chunk_text_overlap():
	unchunked_text = 'abcdefghijklmnopqsrtuvwxyz012345 '
	assert len(SlidingWindowChunker(overlap=True, 
		step_size=21).chunk_text(unchunked_text*512)) == 13

@pytest.mark.unit
def test_serialization():
	step_size = 21
	overlap = True
	chunker = SlidingWindowChunker(overlap=overlap, step_size=step_size)
	assert chunker.id == SlidingWindowChunker.model_validate_json(chunker.model_dump_json()).id
	assert chunker.step_size == step_size
	assert chunker.overlap == overlap

