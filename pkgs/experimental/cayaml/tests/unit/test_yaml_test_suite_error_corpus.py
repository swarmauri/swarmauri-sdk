import json
from pathlib import Path

import pytest

from cayaml import YamlParseError, loads, loads_all


CORPUS_PATH = (
    Path(__file__).resolve().parent.parent
    / "fixtures"
    / "yaml_test_suite_errors.json"
)
ERROR_CASES = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "case",
    ERROR_CASES,
    ids=[case["id"] for case in ERROR_CASES],
)
def test_yaml_test_suite_error_cases_are_rejected(case):
    with pytest.raises(YamlParseError):
        loads(case["yaml"])


@pytest.mark.parametrize(
    "case",
    ERROR_CASES,
    ids=[case["id"] for case in ERROR_CASES],
)
def test_yaml_test_suite_error_streams_are_rejected(case):
    with pytest.raises(YamlParseError):
        loads_all(case["yaml"])
