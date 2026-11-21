from pathlib import Path

import swm_example_plugin

try:
    import tomllib
except ImportError:  # Python 3.10
    import tomli as tomllib


def test_version_matches_pyproject() -> None:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    with pyproject.open("rb") as f:
        version = tomllib.load(f)["project"]["version"]
    assert swm_example_plugin.__version__ == version
