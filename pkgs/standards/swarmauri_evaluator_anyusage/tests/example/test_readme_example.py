"""README-backed usage tests for swarmauri_evaluator_anyusage."""

from pathlib import Path

import pytest

from swarmauri_base.programs.ProgramBase import ProgramBase
from swarmauri_evaluator_anyusage import AnyTypeUsageEvaluator


@pytest.mark.example
def test_readme_usage_example(tmp_path: Path) -> None:
    """Execute the README usage example end-to-end."""

    module = tmp_path / "module.py"
    module.write_text(
        (
            "from typing import Any\n\n"
            "value: Any = 1\n\n"
            "\n"
            "def use(value: Any) -> Any:\n"
            "    return value\n"
        ),
        encoding="utf-8",
    )

    program = ProgramBase()
    program.name = tmp_path.name
    program.path = str(tmp_path)

    evaluator = AnyTypeUsageEvaluator(penalty_per_occurrence=0.1, max_penalty=1.0)
    score, metadata = evaluator.evaluate(program)

    assert score == pytest.approx(0.3)
    assert metadata["files_analyzed"] == 1
    assert metadata["penalty_applied"] == pytest.approx(0.7)
    assert metadata["total_any_occurrences"] == 7

    assert len(metadata["detailed_occurrences"]) == 1
    report = metadata["detailed_occurrences"][0]
    assert report["file"].endswith("module.py")
    contexts = {occurrence["context"] for occurrence in report["occurrences"]}
    assert "from typing import Any" in contexts
    assert "Any used as identifier" in contexts

    for occurrence in report["occurrences"]:
        assert "line" in occurrence
        assert "context" in occurrence
        assert isinstance(occurrence["line"], int)
        assert isinstance(occurrence["context"], str)
