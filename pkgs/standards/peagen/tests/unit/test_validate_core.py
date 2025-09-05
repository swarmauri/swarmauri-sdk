import pytest
from pathlib import Path
from peagen.core.validate_core import _collect_errors, validate_artifact


@pytest.mark.unit
def test_collect_errors_reports_schema_mismatches():
    schema = {
        "type": "object",
        "properties": {"a": {"type": "integer"}},
        "required": ["a"],
    }
    data = {"a": "str"}
    errs = _collect_errors(data, schema)
    assert errs and "a" in errs[0]


@pytest.mark.unit
def test_validate_artifact_unknown_kind(tmp_path: Path):
    result = validate_artifact("unknown", tmp_path)
    assert result["ok"] is False
    assert "unknown kind" in result["errors"][0]
