import pytest
from swarmauri.chunkers.concrete.SentenceChunker import SentenceChunker

@pytest.mark.unit
def test_ubc_resource():
	chunker = SentenceChunker()
	assert chunker.resource == 'Chunker'

@pytest.mark.unit
def test_ubc_type():
	chunker = SentenceChunker()
	assert chunker.type == 'SentenceChunker'

@pytest.mark.unit
def test_chunk_text():
	unchunked_text = 'A walk in the park is a nice start. After the walk, let us talk.'
	chunks = ['A walk in the park is a nice start.', 'After the walk, let us talk.']
	assert SentenceChunker().chunk_text(unchunked_text) == chunks

@pytest.mark.unit
def test_serialization():
	chunker = SentenceChunker()
	assert chunker.id == SentenceChunker.model_validate_json(chunker.model_dump_json()).id