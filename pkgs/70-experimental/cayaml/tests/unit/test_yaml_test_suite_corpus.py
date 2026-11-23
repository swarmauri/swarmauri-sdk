import json
from pathlib import Path

import pytest

from cayaml import loads, loads_all, round_trip_dumps, round_trip_loads_all


CORPUS_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "yaml_test_suite_core.json"
)
CORPUS_CASES = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def expected_documents(case):
    if "json_all" in case:
        return case["json_all"]
    return [case["json"]]


@pytest.mark.parametrize(
    "case",
    CORPUS_CASES,
    ids=[case["id"] for case in CORPUS_CASES],
)
def test_yaml_test_suite_plain_json_expectations(case):
    assert loads(case["yaml"]) == expected_documents(case)[0], case[
        "source_url"
    ]


@pytest.mark.parametrize(
    "case",
    CORPUS_CASES,
    ids=[case["id"] for case in CORPUS_CASES],
)
def test_yaml_test_suite_all_documents_match_json_expectations(case):
    assert loads_all(case["yaml"]) == expected_documents(case), case[
        "source_url"
    ]


@pytest.mark.parametrize(
    "case",
    CORPUS_CASES,
    ids=[case["id"] for case in CORPUS_CASES],
)
def test_yaml_test_suite_round_trip_dump_reloads(case):
    docs = round_trip_loads_all(case["yaml"])
    dumped_docs = [round_trip_dumps(doc) for doc in docs]

    assert [loads(dumped) for dumped in dumped_docs] == expected_documents(
        case
    ), case["source_url"]
