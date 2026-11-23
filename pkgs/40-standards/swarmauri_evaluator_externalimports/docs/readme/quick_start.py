from pathlib import Path
import tempfile
from typing import Any

from swarmauri_core.programs.IProgram import IProgram
from swarmauri_evaluator_externalimports import ExternalImportsEvaluator


class DirectoryProgram(IProgram):
    """Minimal IProgram implementation backed by a filesystem path."""

    def __init__(self, path: str):
        self.path = path

    def diff(self, other: "IProgram"):
        raise NotImplementedError(
            "Diffing is outside the scope of this example"
        )

    def apply_diff(self, diff: Any) -> "IProgram":
        raise NotImplementedError(
            "Diffing is outside the scope of this example"
        )

    def validate(self) -> bool:
        return True

    def clone(self) -> "IProgram":
        return DirectoryProgram(self.path)


def evaluate_example() -> tuple[float, dict[str, Any]]:
    evaluator = ExternalImportsEvaluator()

    with tempfile.TemporaryDirectory() as workdir:
        project = Path(workdir)
        project.joinpath("app.py").write_text(
            """import os\nimport numpy\n\nprint(os.name, numpy.__version__)\n""",
            encoding="utf-8",
        )

        program = DirectoryProgram(workdir)
        score, details = evaluator.evaluate(program)

        print("Score:", score)
        print("External modules:", sorted(details["external_modules"]))
        return score, details


if __name__ == "__main__":
    evaluate_example()
