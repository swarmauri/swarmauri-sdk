from unittest.mock import MagicMock

import pytest

from swarmauri_standard.tools.QueryImageVectorStoreTool import QueryImageVectorStoreTool


@pytest.mark.unit
def test_ubc_resource():
    tool = QueryImageVectorStoreTool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    tool = QueryImageVectorStoreTool()
    assert tool.type == "QueryImageVectorStoreTool"


@pytest.mark.unit
def test_initialization():
    tool = QueryImageVectorStoreTool()
    assert isinstance(tool.id, str)


@pytest.mark.unit
def test_serialization():
    tool = QueryImageVectorStoreTool()
    assert (
        tool.id
        == QueryImageVectorStoreTool.model_validate_json(tool.model_dump_json()).id
    )


@pytest.mark.unit
def test_call_similarity_search():
    mock_store = MagicMock(spec=["similarity_search"])
    mock_store.similarity_search.return_value = [
        {"id": "img1", "score": 0.95, "metadata": {"label": "cat"}},
        {"id": "img2", "score": 0.80, "metadata": {"label": "dog"}},
    ]

    tool = QueryImageVectorStoreTool(vector_store=mock_store)
    results = tool(query="embedding_or_image", top_k=2)

    mock_store.similarity_search.assert_called_once_with(
        "embedding_or_image", top_k=2
    )
    assert len(results) == 2
    assert results[0]["rank"] == 1
    assert results[0]["id"] == "img1"
    assert results[1]["rank"] == 2


@pytest.mark.unit
def test_call_retrieve():
    mock_store = MagicMock(spec=["retrieve"])
    mock_store.retrieve.return_value = [
        {"id": "img1", "score": 0.9},
    ]

    tool = QueryImageVectorStoreTool(vector_store=mock_store)
    results = tool(query="img_query", top_k=1)

    mock_store.retrieve.assert_called_once_with("img_query", top_k=1)
    assert results[0]["rank"] == 1


@pytest.mark.unit
def test_call_with_metadata_filter():
    mock_store = MagicMock(spec=["similarity_search"])
    mock_store.similarity_search.return_value = [
        {"id": "img1", "score": 0.95, "metadata": {"label": "cat"}},
    ]

    tool = QueryImageVectorStoreTool(vector_store=mock_store)
    results = tool(
        query="embedding",
        top_k=1,
        metadata_filter={"label": "cat"},
    )

    mock_store.similarity_search.assert_called_once_with(
        "embedding", top_k=1, metadata_filter={"label": "cat"}
    )
    assert len(results) == 1


@pytest.mark.unit
def test_call_without_vector_store_raises():
    tool = QueryImageVectorStoreTool()
    with pytest.raises(ValueError):
        tool(query="test")
