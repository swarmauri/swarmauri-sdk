import inspect

import pytest
from swarmauri_core.retrievers.IRetriever import IRetriever
from swarmauri_core.vector_stores.IVectorStoreRetrieve import (
    IVectorStoreRetrieve,
)


def test_retriever_is_abstract():
    assert inspect.isabstract(IRetriever)
    with pytest.raises(TypeError):
        IRetriever()


def test_retrieve_signature_is_stable():
    signature = inspect.signature(IRetriever.retrieve)

    assert list(signature.parameters) == ["self", "query", "top_k"]
    assert signature.parameters["top_k"].default == 5


def test_vector_store_retrieve_interface_extends_retriever():
    assert issubclass(IVectorStoreRetrieve, IRetriever)
