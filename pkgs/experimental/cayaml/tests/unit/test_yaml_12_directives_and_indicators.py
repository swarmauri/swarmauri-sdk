from textwrap import dedent

import pytest

from cayaml import YamlParseError, loads, round_trip_dumps, round_trip_loads


def test_directives_accept_separated_comments():
    doc = round_trip_loads(
        dedent(
            """
            %YAML 1.2 # parser version comment
            %TAG !e! tag:example.com,2026: # tag comment
            ---
            value: !e!Thing sample
            """
        )
    )

    assert doc.yaml_version == "1.2"
    assert doc.root.pairs[0][1].tag == "tag:example.com,2026:Thing"
    dumped = round_trip_dumps(doc)
    assert "%YAML 1.2 # parser version comment" in dumped
    assert "%TAG !e! tag:example.com,2026: # tag comment" in dumped


def test_stream_may_start_with_bom_before_directives():
    doc = round_trip_loads(
        "\ufeff%YAML 1.2\n---\nvalue: ok\n",
    )

    assert doc.yaml_version == "1.2"
    assert doc["value"] == "ok"


def test_comments_may_precede_directives():
    doc = round_trip_loads(
        dedent(
            """
            # leading stream comment
            %YAML 1.2
            ---
            value: ok
            """
        )
    )

    assert doc.yaml_version == "1.2"
    assert doc["value"] == "ok"


def test_directives_must_start_at_column_zero():
    with pytest.raises(YamlParseError, match="directive"):
        loads("  %YAML 1.2\n---\nvalue: bad\n")


def test_duplicate_directives_report_parse_errors():
    for source in (
        "%YAML 1.2\n%YAML 1.2\n---\nvalue: bad\n",
        "%TAG !e! tag:example.com,one:\n"
        "%TAG !e! tag:example.com,two:\n"
        "---\nvalue: !e!Thing bad\n",
    ):
        with pytest.raises(YamlParseError, match="directive"):
            loads(source)


def test_undefined_named_tag_handle_reports_parse_error():
    with pytest.raises(YamlParseError, match="undefined tag handle"):
        loads("value: !missing!Thing sample\n")


def test_plain_scalars_can_contain_non_indicator_colons():
    data = loads(
        dedent(
            """
            url: http://example.test/path
            time: 12:30
            scalar: http://example.test/root
            """
        )
    )

    assert data["url"] == "http://example.test/path"
    assert data["time"] == "12:30"
    assert data["scalar"] == "http://example.test/root"


def test_malformed_block_scalar_indicators_report_parse_errors():
    for source in (
        "value: |0\n  bad\n",
        "value: |10\n  bad\n",
        "value: |--\n",
    ):
        with pytest.raises(YamlParseError, match="block scalar"):
            loads(source)


def test_document_markers_require_separation_or_line_end():
    doc = round_trip_loads(
        dedent(
            """
            ---not-marker: value
            ...not-end: kept
            """
        )
    )

    assert doc.has_doc_start is False
    assert doc.has_doc_end is False
    assert doc["---not-marker"] == "value"
    assert doc["...not-end"] == "kept"


def test_question_mark_requires_separation_to_start_explicit_key():
    data = loads(
        dedent(
            """
            ?plain: block value
            explicit:
              ? separated
              : explicit value
            flow: {?plain: flow value, ? separated: explicit flow value}
            """
        )
    )

    assert data["?plain"] == "block value"
    assert data["explicit"] == {"separated": "explicit value"}
    assert data["flow"] == {
        "?plain": "flow value",
        "separated": "explicit flow value",
    }


def test_tabs_are_rejected_in_indentation():
    with pytest.raises(YamlParseError, match="tab"):
        loads("root:\n\tchild: bad\n")
