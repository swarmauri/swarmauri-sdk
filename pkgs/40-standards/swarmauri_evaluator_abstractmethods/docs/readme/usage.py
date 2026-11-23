import textwrap
from typing import Dict

from swarmauri_core.programs.IProgram import DiffType, IProgram
from swarmauri_evaluator_abstractmethods import AbstractMethodsEvaluator


class InMemoryProgram(IProgram):
    def __init__(self, files: Dict[str, str]):
        self._files = files

    def diff(self, other: IProgram) -> DiffType:
        return {}

    def apply_diff(self, diff: DiffType) -> IProgram:
        return self

    def validate(self) -> bool:
        return True

    def clone(self) -> IProgram:
        return InMemoryProgram(dict(self._files))

    def get_source_files(self) -> Dict[str, str]:
        return self._files


def main() -> None:
    program = InMemoryProgram(
        {
            "shapes.py": textwrap.dedent(
                """
                from abc import ABC, abstractmethod

                class Shape(ABC):
                    @abstractmethod
                    def area(self):
                        ...
                """
            ).strip(),
            "incomplete.py": textwrap.dedent(
                """
                from abc import ABC

                class InvalidShape(ABC):
                    def area(self):
                        ...
                """
            ).strip(),
        }
    )

    evaluator = AbstractMethodsEvaluator()
    score, metadata = evaluator.evaluate(program)

    print(f"Score: {score:.2f}")
    for issue in metadata["issues"]:
        if not issue["has_abstractmethod"]:
            print(f"{issue['file']}:{issue['line']} -> {issue['message']}")


if __name__ == "__main__":
    main()
