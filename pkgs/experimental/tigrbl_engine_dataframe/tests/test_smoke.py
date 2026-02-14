from pathlib import Path


def test_package_assets_present() -> None:
    package_dir = Path(__file__).resolve().parents[1]
    assert (package_dir / "README.md").is_file()
    assert (package_dir / "LICENSE").is_file()
    assert (package_dir / "pyproject.toml").is_file()
