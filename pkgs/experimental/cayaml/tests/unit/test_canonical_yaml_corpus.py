from textwrap import dedent

import pytest

from cayaml import dumps, loads, loads_all, round_trip_dumps, round_trip_loads
from cayaml.ast_nodes import DocumentNode


CANONICAL_FEATURE_CORPUS = dedent(
    """
    %YAML 1.2
    %TAG ! tag:example.com,2026:app/
    ---
    defaults: &defaults
      name: DefaultName
      enabled: true
      tags:
        - alpha
        - beta
      note: |
        Line one
        Line two

    override: &override
      name: OverrideName
      count: 7

    merged:
      <<: [*defaults, *override]
      enabled: false
      extra: CafÃ© ðŸ˜€

    copied: *defaults
    typed: &typed !!str "hello"
    typed_copy: *typed
    folded: >
      folded text
      stays readable
    inline: value # preserve this comment
    ...
    ---
    list:
      - &first item one
      - *first
      - |
        block item
    """
)

UPSTREAM_STYLE_CONFORMANCE_CASES = [
    {
        "id": "plain-scalar-nested-continuation",
        "source": "key:\n  first\n  second\n",
        "expected": {"key": "first second"},
        "reference": "yaml-test-suite block scalar/flow-in block parity",
    },
    {
        "id": "plain-scalar-blank-line-continuation",
        "source": "key:\n  first\n\n  second\n",
        "expected": {"key": "first\nsecond"},
        "reference": "yaml-test-suite folded plain scalar continuation",
    },
    {
        "id": "explicit-key-comment-before-value",
        "source": "? key\n# value comment\n: value\n",
        "expected": {"key": "value"},
        "reference": "yaml-test-suite explicit key separation",
    },
    {
        "id": "explicit-key-indented-comment-before-value",
        "source": "? key\n  # value comment\n: value\n",
        "expected": {"key": "value"},
        "reference": "yaml-test-suite explicit key separation",
    },
]


@pytest.mark.parametrize(
    "case",
    UPSTREAM_STYLE_CONFORMANCE_CASES,
    ids=[case["id"] for case in UPSTREAM_STYLE_CONFORMANCE_CASES],
)
def test_upstream_style_conformance_cases(case):
    assert loads(case["source"]) == case["expected"], case["reference"]


def test_canonical_feature_corpus_plain_loads():
    data = loads(CANONICAL_FEATURE_CORPUS)

    assert data["merged"]["name"] == "OverrideName"
    assert data["merged"]["enabled"] is False
    assert data["merged"]["count"] == 7
    assert data["merged"]["tags"] == ["alpha", "beta"]
    assert data["merged"]["note"] == "Line one\nLine two\n"
    assert data["merged"]["extra"] == "CafÃ© ðŸ˜€"
    assert isinstance(data["copied"], dict)
    assert data["copied"]["name"] == "DefaultName"
    assert data["typed"] == "hello"
    assert data["typed_copy"] == "hello"
    assert data["folded"] == "folded text stays readable\n"


def test_canonical_feature_corpus_plain_loads_all():
    docs = loads_all(CANONICAL_FEATURE_CORPUS)

    assert len(docs) == 2
    assert docs[0]["merged"]["name"] == "OverrideName"
    assert docs[1]["list"] == ["item one", "item one", "block item\n"]


def test_canonical_feature_corpus_round_trip_loads():
    doc = round_trip_loads(CANONICAL_FEATURE_CORPUS)

    assert isinstance(doc, DocumentNode)
    assert doc.has_doc_start is True
    assert doc.has_doc_end is True
    assert doc["merged"]["name"] == "OverrideName"
    assert doc["copied"]["tags"] == ["alpha", "beta"]
    assert doc["typed_copy"] == "hello"
    assert doc["folded"].style == ">"
    assert doc["inline"] == "value"


def test_canonical_feature_corpus_round_trip_dump_preserves_surface_markers():
    doc = round_trip_loads(CANONICAL_FEATURE_CORPUS)
    dumped = round_trip_dumps(doc)

    assert "---" in dumped
    assert "..." in dumped
    assert "<<:" in dumped
    assert "# preserve this comment" in dumped
    assert "note: |" in dumped
    assert "folded: >" in dumped
    assert "*defaults" in dumped


def test_canonical_feature_corpus_dumps_ast_with_comments():
    doc = round_trip_loads(CANONICAL_FEATURE_CORPUS)
    dumped = dumps(doc)

    assert "# preserve this comment" in dumped
    assert "folded: >" in dumped
