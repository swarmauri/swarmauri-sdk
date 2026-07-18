from typing import List

import pytest
from swarmauri_base.retrievers.RetrieverBase import RetrieverBase
from swarmauri_base.retrievers.RetrieverMixin import RetrieverMixin
from swarmauri_core.documents.IDocument import IDocument


class ConcreteRetriever(RetrieverBase):
    def retrieve(self, query: str, top_k: int = 5) -> List[IDocument]:
        return []


def test_retriever_base_is_not_instantiable():
    assert RetrieverBase.model_fields["type"].default == "RetrieverBase"
    with pytest.raises(TypeError):
        RetrieverBase()


def test_concrete_retriever_has_resource_and_type():
    retriever = ConcreteRetriever()

    assert retriever.resource == "Retriever"
    assert retriever.type == "ConcreteRetriever"


def test_concrete_retriever_roundtrips_json():
    original = ConcreteRetriever(name="example")

    restored = ConcreteRetriever.model_validate_json(
        original.model_dump_json()
    )

    assert restored.name == original.name
    assert restored.resource == "Retriever"
    assert restored.type == "ConcreteRetriever"


def test_retriever_mixin_is_not_a_component_base():
    assert not issubclass(RetrieverMixin, RetrieverBase)
