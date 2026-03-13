from pathlib import Path

import tomllib


def test_tigrbl_base_does_not_depend_on_tigrbl_package() -> None:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    dependencies = data["project"]["dependencies"]

    assert "tigrbl" not in dependencies
    assert all(not dep.startswith("tigrbl==") for dep in dependencies)
