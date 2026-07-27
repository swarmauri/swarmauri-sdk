
import pytest
from pydantic import BaseModel
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.retrievers.IRetriever import IRetriever

from swarmauri_base.retrievers.RetrieverMixin import RetrieverMixin


class ConcreteMixinRetriever(RetrieverMixin):
    def retrieve(self, query: str, top_k: int = 5) -> list[IDocument]:
        return []


def test_retriever_mixin_implements_retriever_contract():
    assert issubclass(RetrieverMixin, IRetriever)
    assert ConcreteMixinRetriever().retrieve("query") == []


@pytest.mark.unit
def test_vector_store_retrieve_mixin_uses_interface_and_basemodel():
    from swarmauri_core.vector_stores.IVectorStoreRetrieve import (
        IVectorStoreRetrieve,
    )

    from swarmauri_base.vector_stores.VectorStoreRetrieveMixin import (
        VectorStoreRetrieveMixin,
    )

    assert VectorStoreRetrieveMixin.__bases__ == (
        IVectorStoreRetrieve,
        BaseModel,
    )
