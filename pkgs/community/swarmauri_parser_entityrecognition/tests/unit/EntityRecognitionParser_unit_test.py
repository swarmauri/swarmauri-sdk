import pytest
from swarmauri_parser_entityrecognition.EntityRecognitionParser import (
    EntityRecognitionParser as Parser,
)


@pytest.fixture(scope="module")
def parser():
    """Fixture to provide a parser instance for tests."""
    return Parser()


@pytest.mark.unit
def test_ubc_resource(parser):
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type(parser):
    assert parser.type == "EntityRecognitionParser"


@pytest.mark.unit
def test_serialization(parser):
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse(parser):
    # Test with text containing known entities
    text = "John works at Apple in New York."
    documents = parser.parse(text)

    # Verify documents were created
    assert len(documents) == 3

    # Create entity map for easy testing
    entity_map = {doc.content: doc.metadata["entity_type"] for doc in documents}

    # Verify expected entities and their types
    assert "John" in entity_map
    assert entity_map["John"] == "PERSON"
    assert "Apple" in entity_map
    assert entity_map["Apple"] == "ORG"
    assert "New York" in entity_map
    assert entity_map["New York"] == "GPE"

    # Verify document structure
    for doc in documents:
        assert doc.resource == "Document"
        assert isinstance(doc.content, str)
        assert "entity_type" in doc.metadata


@pytest.mark.unit
def test_parse_empty(parser):
    documents = parser.parse("")
    assert len(documents) == 0


@pytest.mark.unit
def test_parse_no_entities(parser):
    documents = parser.parse("The quick brown fox.")
    assert len(documents) == 0


@pytest.mark.unit
def test_parse_multiple_same_entity(parser):
    documents = parser.parse("John met John in Paris.")
    assert len(documents) == 3  # 2 PERSONs + 1 GPE
