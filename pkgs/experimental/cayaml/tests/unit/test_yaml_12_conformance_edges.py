from textwrap import dedent

import pytest

from cayaml import (
    YamlParseError,
    dumps,
    loads,
    loads_all,
    round_trip_dumps,
    round_trip_loads,
)
from cayaml.ast_nodes import MappingNode, SequenceNode


def test_yaml_12_tag_directives_and_custom_tag_expansion():
    doc = round_trip_loads(
        dedent(
            """
            %YAML 1.2
            %TAG !e! tag:example.com,2026:
            ---
            canonical: !<tag:yaml.org,2002:str> 42
            shorthand: !e!Thing {name: sample, count: !!int "2"}
            local: !local [a, b]
            bool_value: !!bool "false"
            ...
            """
        )
    )

    assert doc.yaml_version == "1.2"
    assert doc.tag_handles["!e!"] == "tag:example.com,2026:"
    assert doc.root.pairs[0][1].tag == "tag:yaml.org,2002:str"
    assert doc["canonical"] == "42"
    assert doc.root.pairs[1][1].tag == "tag:example.com,2026:Thing"
    assert doc["shorthand"] == {"name": "sample", "count": 2}
    assert doc.root.pairs[2][1].tag == "!local"
    assert doc["local"] == ["a", "b"]
    assert doc["bool_value"] is False

    dumped = round_trip_dumps(doc)
    assert "%YAML 1.2" in dumped
    assert "%TAG !e! tag:example.com,2026:" in dumped
    assert "!<tag:yaml.org,2002:str> 42" in dumped
    assert "!e!Thing {name: sample, count: !!int 2}" in dumped


def test_block_scalar_indentation_indicators_and_chomping_edges():
    data = loads(
        dedent(
            """
            literal_auto: |
              first
                deeper
            literal_indent: |2-
                kept indent
                  deeper
            folded_indent: >2
              folded
              text

                more indented
            """
        )
    )

    assert data["literal_auto"] == "first\n  deeper\n"
    assert data["literal_indent"] == "  kept indent\n    deeper"
    assert data["folded_indent"] == "folded text\n\n  more indented\n"


def test_block_scalars_preserve_leading_blank_lines():
    data = loads(
        dedent(
            """
            literal: |

              first

              second
            folded: >

              first

              second
            """
        )
    )

    assert data["literal"] == "\nfirst\n\nsecond\n"
    assert data["folded"] == "\nfirst\nsecond\n"


def test_advanced_folded_scalar_rules_preserve_more_indented_lines():
    data = loads(
        dedent(
            """
            folded: >
              paragraph line one
              paragraph line two

                literal-ish line
                second literal-ish line

              next paragraph
            """
        )
    )

    assert data["folded"] == (
        "paragraph line one paragraph line two\n\n"
        "  literal-ish line\n"
        "  second literal-ish line\n\n"
        "next paragraph\n"
    )


def test_folded_block_scalar_blank_lines_and_tab_content_edges():
    docs = loads_all(
        "--- >\n"
        " ab\n"
        " cd\n"
        " \n"
        " ef\n"
        "\n"
        "\n"
        " gh\n"
        "--- >\n"
        " \n"
        "  # detected\n"
        "--- >\n"
        " \t\n"
        " detected\n"
    )

    assert docs == [
        "ab cd\nef\n\ngh\n",
        "\n# detected\n",
        "\t\ndetected\n",
    ]


def test_quoted_multiline_scalars_fold_yaml_12_whitespace_edges():
    data = loads(
        'escaped_tab: "trailing\\\t  \n'
        '    tab"\n'
        'trailing_tab: "trailing\t  \n'
        '    tab"\n'
        "blank_single: '\n"
        "\n"
        "  '\n"
        'blank_double: "\n'
        "\n"
        "\n"
        '  "\n'
        'continuation: "folded\n'
        "  to a space,\n"
        "   \n"
        "  to a line feed, or \t\\\n"
        '   \\ \tnon-content"\n'
    )

    assert data["escaped_tab"] == "trailing\t tab"
    assert data["trailing_tab"] == "trailing tab"
    assert data["blank_single"] == "\n"
    assert data["blank_double"] == "\n\n"
    assert data["continuation"] == (
        "folded to a space,\nto a line feed, or \t \tnon-content"
    )


def test_property_only_lines_and_one_space_indentation_are_valid():
    data = loads(
        dedent(
            """
            seq:
             &anchor
            - a
            - b
            mapping:
             key: value
            tagged_seq: !!seq
            - entry
            - !!seq
             - nested
            """
        )
    )

    assert data == {
        "seq": ["a", "b"],
        "mapping": {"key": "value"},
        "tagged_seq": ["entry", ["nested"]],
    }


def test_tag_handle_override_and_binary_normalization():
    data = loads(
        dedent(
            """
            %TAG !! tag:example.com,2000:app/
            ---
            custom: !!int 1 - 3 # Not the core integer tag.
            binary: !!binary "\\
             SGVs\\
             bG8="
            """
        )
    )

    assert data["custom"] == "1 - 3"
    assert data["binary"] == "SGVsbG8="


def test_complex_mapping_keys_round_trip_and_plain_conversion():
    data = loads(
        dedent(
            """
            ? {name: api, version: 1}
            : mapping key value
            ? - region
              - us-east
            : sequence key value
            ? !!str 42
            : string key value
            ? [compact, sequence]: compact sequence key value
            ? {compact: mapping}: compact mapping key value
            ? compact null:
            """
        )
    )

    assert data[(("name", "api"), ("version", 1))] == "mapping key value"
    assert data[("region", "us-east")] == "sequence key value"
    assert data["42"] == "string key value"
    assert data[("compact", "sequence")] == "compact sequence key value"
    assert data[(("compact", "mapping"),)] == "compact mapping key value"
    assert data["compact null"] is None

    doc = round_trip_loads(
        dedent(
            """
            ? {name: api, version: 1}
            : mapping key value
            ? [region, us-east]
            : sequence key value
            """
        )
    )
    assert isinstance(doc.root.pairs[0][0], MappingNode)
    assert isinstance(doc.root.pairs[1][0], SequenceNode)
    dumped = round_trip_dumps(doc)
    assert "? {name: api, version: 1}" in dumped
    assert "? [region, us-east]" in dumped


@pytest.mark.parametrize(
    "yaml_text,error_match",
    [
        ("key: [unterminated\n", "flow collection"),
        ("key: {missing: value\n", "flow collection"),
        ("key: value\n  - orphan\n", "mapping indentation"),
        ("key:\n\tchild: bad\n", "tab"),
        ("key: *missing\n", "undefined alias"),
        ("%YAML nope\n---\nkey: value\n", "YAML directive"),
        ("%TAG !e!\n---\nkey: value\n", "TAG directive"),
        ("key: !!int nope\n", "tag !!int"),
    ],
)
def test_malformed_yaml_reports_specific_parse_errors(yaml_text, error_match):
    with pytest.raises(YamlParseError, match=error_match):
        loads(yaml_text)


def test_emitter_round_trips_conformance_corpus_surface_markers():
    source = dedent(
        """
        %YAML 1.2
        %TAG !e! tag:example.com,2026:
        ---
        tagged: !e!Thing {name: sample}
        explicit:
          ? [compound, key]
          : value
        text: >-
          folded
          text
        literal: |2
            kept
        ...
        """
    )

    doc = round_trip_loads(source)
    dumped = round_trip_dumps(doc)

    assert "%YAML 1.2" in dumped
    assert "%TAG !e! tag:example.com,2026:" in dumped
    assert "tagged: !e!Thing {name: sample}" in dumped
    assert "? [compound, key]" in dumped
    assert "text: >-" in dumped
    assert "literal: |2" in dumped
    assert dumped.strip().endswith("...")
    assert loads(dumps(loads(dumped)))["tagged"] == {"name": "sample"}
