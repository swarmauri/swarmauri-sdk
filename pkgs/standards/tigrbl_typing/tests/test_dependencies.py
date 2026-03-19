from pathlib import Path
import tomllib


def test_project_declares_expected_runtime_dependencies() -> None:
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

    assert pyproject["project"]["dependencies"] == ["pydantic>=2.10,<3"]
