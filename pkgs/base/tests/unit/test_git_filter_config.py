"""Regression coverage for standalone Git-filter configuration."""

from swarmauri_base.git_filters.config import load_filter_config


def test_read_parent_configuration(tmp_path, monkeypatch):
    (tmp_path / "peagen.toml").write_text(
        '[storage.filters.s3fs]\nregion = "test"'
    )
    child = tmp_path / "child"
    child.mkdir()
    monkeypatch.delenv("PEAGEN_CONFIG", raising=False)
    monkeypatch.chdir(child)
    assert (
        load_filter_config()["storage"]["filters"]["s3fs"]["region"] == "test"
    )


def test_explicit_configuration(tmp_path, monkeypatch):
    path = tmp_path / "custom.toml"
    path.write_text("value = 42")
    monkeypatch.setenv("PEAGEN_CONFIG", str(path))
    assert load_filter_config() == {"value": 42}
