"""Execute the README usage example to ensure it stays in sync."""

import pytest

from swarmauri_parser_keywordextractor import KeywordExtractorParser


@pytest.mark.example
@pytest.mark.parametrize(
    "text",
    [
        "Artificial intelligence and machine learning are transforming technology",
    ],
)
def test_readme_usage_example(text: str) -> None:
    parser = KeywordExtractorParser(num_keywords=3, lang="en")

    documents = parser.parse(text)

    assert len(documents) == 3
    for document in documents:
        assert document.content
        assert "score" in document.metadata
        score = document.metadata["score"]
        assert score is not None
        float(score)
