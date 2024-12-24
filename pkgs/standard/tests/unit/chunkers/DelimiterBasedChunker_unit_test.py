import pytest
from swarmauri.chunkers.concrete.DelimiterBasedChunker import DelimiterBasedChunker

@pytest.mark.unit
def test_ubc_resource():
	chunker = DelimiterBasedChunker()
	assert chunker.resource == 'Chunker'

@pytest.mark.unit
def test_ubc_type():
	chunker = DelimiterBasedChunker()
	assert chunker.type == 'DelimiterBasedChunker'

@pytest.mark.unit
def test_chunk_text():
	unchunked_text = 'question? test! period. run on'
	chunks = ['question?', 'test!', 'period.', 'run on']
	assert DelimiterBasedChunker().chunk_text(unchunked_text) == chunks

@pytest.mark.unit
def test_serialization():
	chunker = DelimiterBasedChunker()
	assert chunker.id == DelimiterBasedChunker.model_validate_json(chunker.model_dump_json()).id


