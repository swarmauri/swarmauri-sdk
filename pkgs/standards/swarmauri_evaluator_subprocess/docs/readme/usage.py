from pathlib import Path
import tempfile

from swarmauri_evaluator_subprocess import SubprocessEvaluator
from swarmauri_core.programs.IProgram import DiffType, IProgram


class ScriptProgram(IProgram):
    """Minimal IProgram wrapper for a script stored on disk."""

    def __init__(self, path: Path):
        self._path = Path(path)

    # Required IProgram interface methods -------------------------------
    def diff(self, other: IProgram) -> DiffType:  # pragma: no cover - example
        return {}

    def apply_diff(
        self, diff: DiffType
    ) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    def validate(self) -> bool:  # pragma: no cover
        return self._path.exists()

    def clone(self) -> "ScriptProgram":  # pragma: no cover
        return ScriptProgram(self._path)

    # Methods consumed by SubprocessEvaluator ---------------------------
    def get_path(self) -> str:
        return str(self._path)

    def is_executable(self) -> bool:
        return False


def run_example(expected_output: str = "hello from subprocess\n"):
    evaluator = SubprocessEvaluator(timeout=5)

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = Path(tmpdir) / "echo.py"
        script_path.write_text(
            "print('hello from subprocess')\n", encoding="utf-8"
        )

        program = ScriptProgram(script_path)

        score, metadata = evaluator.evaluate(
            program,
            expected_output=expected_output,
        )

    return score, metadata


def main():
    score, metadata = run_example()
    print("Score:", score)
    print("Stdout:", metadata["stdout"].strip())
    print("Reason:", metadata["reason"])


if __name__ == "__main__":
    main()
