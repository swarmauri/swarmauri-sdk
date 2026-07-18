from typing import List

from swarmauri_base.retrievers.RetrieverMixin import RetrieverMixin
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_core.retrievers.IRetriever import IRetriever


class ConcreteMixinRetriever(RetrieverMixin):
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        return []


def test_retriever_mixin_implements_retriever_contract():
    assert issubclass(RetrieverMixin, IRetriever)
    assert ConcreteMixinRetriever().retrieve("query") == []
