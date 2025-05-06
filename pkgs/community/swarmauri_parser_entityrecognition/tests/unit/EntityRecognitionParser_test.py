import pytest
from swarmauri_parser_entityrecognition.EntityRecognitionParser import (
    EntityRecognitionParser as Parser,
)

from swarmauri_standard.documents.Document import Document


@pytest.fixture(scope="module")
def parser():
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
    sample_text = "Apple Inc. is planning to open a new office in New York City, according to CEO Tim Cook."

    results = parser.parse(sample_text)

    assert isinstance(results, list)
    assert len(results) > 0

    for doc in results:
        assert isinstance(doc, Document)
        assert "entity_type" in doc.metadata
        assert doc.content in sample_text

    entity_texts = [doc.content for doc in results]
    entity_types = [doc.metadata["entity_type"] for doc in results]

    expected_entities = {
        "Apple Inc.": "ORG",
        "New York City": "GPE",
        "Tim Cook": "PERSON",
    }

    for entity, expected_type in expected_entities.items():
        matches = [
            i for i, text in enumerate(entity_texts) if entity in text or text in entity
        ]

        if matches:
            idx = matches[0]
            assert entity_types[idx] in [
                expected_type,
                "PERSON",
                "ORG",
                "GPE",
                "LOC",
            ], (
                f"Expected entity '{entity}' to be recognized as {expected_type} or similar"
            )

    number_result = parser.parse(42)
    assert isinstance(number_result, list)
