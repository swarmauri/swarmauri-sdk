import pytest
from swarmauri.documents.concrete.Document import Document


@pytest.mark.unit
def test_ubc_resource():
    document = Document(content="test")
    assert document.resource == "Document"


@pytest.mark.unit
def test_ubc_type():
    assert Document(content="test").type == "Document"


@pytest.mark.unit
def test_serialization():
    document = Document(content="test")
    assert document.id == Document.model_validate_json(document.model_dump_json()).id


@pytest.mark.unit
def test_content():
    document = Document(content="test")
    assert document.content == "test"
