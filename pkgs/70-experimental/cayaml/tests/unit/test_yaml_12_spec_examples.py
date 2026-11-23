from textwrap import dedent

from cayaml import loads, loads_all, round_trip_dumps, round_trip_loads
from cayaml.ast_nodes import ScalarNode


def test_indentless_sequences_as_mapping_values():
    data = loads(
        dedent(
            """
            american:
            - Boston Red Sox
            - Detroit Tigers
            national:
            - New York Mets
            - Chicago Cubs
            """
        )
    )

    assert data == {
        "american": ["Boston Red Sox", "Detroit Tigers"],
        "national": ["New York Mets", "Chicago Cubs"],
    }


def test_compact_nested_block_sequences():
    data = loads(
        dedent(
            """
            matrix:
              - - one
                - two
              - - three
                - four
            """
        )
    )

    assert data["matrix"] == [["one", "two"], ["three", "four"]]


def test_document_start_can_carry_root_node_on_same_line():
    docs = loads_all(
        dedent(
            """
            --- [one, two]
            --- {three: four}
            --- !!str 42
            """
        )
    )

    assert docs == [["one", "two"], {"three": "four"}, "42"]


def test_json_documents_are_valid_yaml_12_documents():
    docs = loads_all(
        dedent(
            """
            --- {"name":"alpha","enabled":true}
            --- [1,2,3]
            --- "json string"
            --- null
            """
        )
    )

    assert docs == [
        {"name": "alpha", "enabled": True},
        [1, 2, 3],
        "json string",
        None,
    ]


def test_root_scalar_documents_and_block_scalar_documents():
    plain_doc = round_trip_loads("--- bare scalar")
    literal_doc = round_trip_loads(
        dedent(
            """
            --- |
              Mark McGwire's
              year was crippled
              by a knee injury.
            """
        )
    )
    folded_doc = round_trip_loads(
        dedent(
            """
            --- >
              Sammy Sosa completed another
              fine season with great stats.
            """
        )
    )

    assert plain_doc.root == ScalarNode("bare scalar")
    assert literal_doc.root == (
        "Mark McGwire's\nyear was crippled\nby a knee injury.\n"
    )
    assert folded_doc.root == (
        "Sammy Sosa completed another fine season with great stats.\n"
    )
    assert round_trip_dumps(plain_doc).startswith("--- bare scalar")
    assert "--- |" in round_trip_dumps(literal_doc)
    assert "--- >" in round_trip_dumps(folded_doc)


def test_multiline_flow_collection_and_scalar_folding():
    data = loads(
        dedent(
            """
            flow:
              [
                Detroit Tigers,
                Chicago Cubs,
                {name: Mark McGwire, hr: 65}
              ]
            quoted: "Sammy
              Sosa"
            single_quoted: 'Sammy
              Sosa''s season'
            plain: Sammy
              Sosa
            """
        )
    )

    assert data["flow"] == [
        "Detroit Tigers",
        "Chicago Cubs",
        {"name": "Mark McGwire", "hr": 65},
    ]
    assert data["quoted"] == "Sammy Sosa"
    assert data["single_quoted"] == "Sammy Sosa's season"
    assert data["plain"] == "Sammy Sosa"


def test_round_trip_emitter_preserves_document_start_inline_roots():
    for source in ("--- [one, two]", "--- {three: four}", "--- !!str 42"):
        dumped = round_trip_dumps(round_trip_loads(source))
        assert dumped == source
