import pytest
from swarmauri.standard.documents.concrete.Document import Document

@pytest.mark.unit
def test_ubc_resource():
	document = Document(content="test")
	assert document.resource == 'Document'

@pytest.mark.unit
def test_ubc_type():
    assert Document(content="test").type == 'Document'

@pytest.mark.unit
def test_serialization():
	document = Document(content="test")
    assert document.id == Document.model_validate_json(document.json()).id

@pytest.mark.unit
def content_test():
	document = Document(content="test")
	assert document.content == 'test'