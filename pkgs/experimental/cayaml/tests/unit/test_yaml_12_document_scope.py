from textwrap import dedent

import pytest

from cayaml import (
    YamlParseError,
    loads,
    loads_all,
    round_trip_dumps,
    round_trip_loads,
    round_trip_loads_all,
)


def test_anchors_are_scoped_to_each_document():
    with pytest.raises(YamlParseError, match="undefined alias"):
        loads_all(
            dedent(
                """
                ---
                first: &anchor value
                ---
                second: *anchor
                """
            )
        )


def test_reused_anchors_retarget_alias_to_most_recent_node():
    data = loads(
        dedent(
            """
            first: &same one
            first_alias: *same
            second: &same two
            second_alias: *same
            """
        )
    )

    assert data["first_alias"] == "one"
    assert data["second_alias"] == "two"


def test_tag_handles_are_scoped_to_each_document():
    docs = round_trip_loads_all(
        dedent(
            """
            %TAG !a! tag:example.com,a/
            ---
            value: !a!Thing one
            """
        )
    )

    assert docs[0].root.pairs[0][1].tag == "tag:example.com,a/Thing"
    assert docs[0].tag_handles == {"!a!": "tag:example.com,a/"}


def test_undefined_named_tag_handles_are_errors_per_document_scope():
    with pytest.raises(YamlParseError, match="undefined tag handle"):
        round_trip_loads_all(
            dedent(
                """
                %TAG !a! tag:example.com,a/
                ---
                value: !a!Thing one
                ---
                value: !a!Thing two
                """
            )
        )


def test_reserved_directives_are_preserved_without_semantic_effect():
    docs = round_trip_loads_all(
        dedent(
            """
            %YAML 1.2
            %FOO one two
            ---
            key: value
            """
        )
    )

    assert docs[0]["key"] == "value"
    assert docs[0].directives == ["%YAML 1.2", "%FOO one two"]
    dumped = round_trip_dumps(docs[0])
    assert "%FOO one two" in dumped


def test_empty_documents_resolve_to_null_in_plain_mode():
    assert loads("---\n...\n") is None
    assert loads_all("---\n...\n---\nvalue\n") == [None, "value"]


def test_empty_documents_preserve_markers_in_round_trip_mode():
    doc = round_trip_loads("---\n...\n")

    assert doc.root is None
    assert doc.has_doc_start is True
    assert doc.has_doc_end is True
    assert round_trip_dumps(doc) == "---\n..."


def test_extra_top_level_content_after_root_node_is_error():
    for source in (
        "scalar root\nmapping: value\n",
        "[flow, root]\nextra: value\n",
        "&root [a, b]\ncopy: *root\n",
    ):
        with pytest.raises(YamlParseError, match="document root"):
            loads(source)


def test_merge_aliases_must_exist_and_resolve_to_mappings():
    for source, error_match in (
        ("merged:\n  <<: *missing\n", "undefined alias"),
        ("base: &base [not, mapping]\nmerged:\n  <<: *base\n", "merge"),
        ("base: &base scalar\nmerged:\n  <<: *base\n", "merge"),
    ):
        with pytest.raises(YamlParseError, match=error_match):
            loads(source)


def test_alias_nodes_cannot_have_properties_or_content():
    for source in (
        "base: &a 1\nref: !!str *a\n",
        "base: &a 1\nref: &b *a\n",
        "base: &a 1\nref: *a extra\n",
    ):
        with pytest.raises(YamlParseError, match="alias"):
            loads(source)


def test_anchor_and_alias_names_must_be_non_empty_and_flow_safe():
    for source, error_match in (
        ("value: & kept\n", "anchor"),
        ("value: &bad,name kept\n", "anchor"),
        ("value: &bad[ kept\n", "anchor"),
        ("value: *bad,name\n", "alias"),
    ):
        with pytest.raises(YamlParseError, match=error_match):
            loads(source)
