import pytest
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.concrete.BeautifulSoupElementParser import (
    BeautifulSoupElementParser as Parser,
)


@pytest.mark.unit
def test_ubc_resource():
    html_content = "<div><p>Sample HTML content</p></div>"
    parser = Parser(element=html_content)
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type():
    html_content = "<div><p>Sample HTML content</p></div>"
    assert Parser(element=html_content).type == "BeautifulSoupElementParser"


@pytest.mark.unit
def test_initialization():
    html_content = "<div><p>Sample HTML content</p></div>"
    parser = Parser(element=html_content)
    assert type(parser.id) == str


@pytest.mark.unit
def test_serialization():
    html_content = "<div><p>Sample HTML content</p></div>"
    parser = Parser(element=html_content)
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.parametrize(
    "html_content, element, expected_count, expected_content",
    [
        (
            "<div><p>First paragraph</p><p>Second paragraph</p></div>",
            "p",
            2,
            ["<p>First paragraph</p>", "<p>Second paragraph</p>"],
        ),
        (
            "<div><span>Some span content</span></div>",
            "span",
            1,
            ["<span>Some span content</span>"],
        ),
        ("<div><h1>Header</h1><p>Paragraph</p></div>", "h1", 1, ["<h1>Header</h1>"]),
        ("<div>No matching tags here</div>", "a", 0, []),
    ],
)
@pytest.mark.unit
def test_parse(html_content, element, expected_count, expected_content):
    parser = Parser(element=element)

    documents = parser.parse(html_content)

    assert isinstance(documents, list), "The result should be a list."
    assert (
        len(documents) == expected_count
    ), f"Expected {expected_count} documents, got {len(documents)}."
    assert all(
        isinstance(doc, Document) for doc in documents
    ), "All items in the result should be Document instances."
    assert [
        doc.content for doc in documents
    ] == expected_content, (
        "The content of documents does not match the expected content."
    )
