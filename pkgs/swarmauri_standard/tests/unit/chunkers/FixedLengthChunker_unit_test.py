import pytest

from swarmauri_standard.chunkers.FixedLengthChunker import FixedLengthChunker


@pytest.mark.unit
def test_ubc_resource():
    chunker = FixedLengthChunker()
    assert chunker.resource == "Chunker"


@pytest.mark.unit
def test_ubc_type():
    chunker = FixedLengthChunker()
    assert chunker.type == "FixedLengthChunker"


@pytest.mark.unit
def test_chunk_text():
    assert len(FixedLengthChunker().chunk_text("ab " * 512)) == 6


@pytest.mark.unit
def test_chunk_text_fixed_length():
    chunker = FixedLengthChunker(chunk_size=2)
    assert chunker.chunk_text("abcde") == ["ab", "cd", "e"]


@pytest.mark.unit
@pytest.mark.parametrize("chunk_size", [0, -1])
def test_invalid_chunk_size(chunk_size):
    with pytest.raises(
        ValueError, match="chunk_size must be a positive integer"
    ) as exc_info:
        FixedLengthChunker(chunk_size=chunk_size)
    assert type(exc_info.value) is ValueError


@pytest.mark.unit
def test_serialization():
    chunker = FixedLengthChunker()
    assert (
        chunker.id
        == FixedLengthChunker.model_validate_json(chunker.model_dump_json()).id
    )
