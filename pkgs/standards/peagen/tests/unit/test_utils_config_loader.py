import pytest
from peagen._utils.config_loader import (
    _expand_env_in_text,
    _expand_env_vars,
    _merge,
    load_peagen_toml,
)


@pytest.mark.unit
def test_expand_env_in_text(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    assert _expand_env_in_text('name="${FOO}"') == 'name="bar"'


@pytest.mark.unit
def test_expand_env_vars(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    data = {"val": "${FOO}"}
    assert _expand_env_vars(data) == {"val": "bar"}


@pytest.mark.unit
def test_merge_nested_dicts():
    a = {"a": {"b": 1}, "x": 2}
    b = {"a": {"c": 3}, "y": 4}
    result = _merge(a, b)
    assert result == {"a": {"b": 1, "c": 3}, "x": 2, "y": 4}
    assert a == {"a": {"b": 1}, "x": 2}


@pytest.mark.unit
def test_load_peagen_toml(tmp_path, monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    cfg_file = tmp_path / "cfg.toml"
    cfg_file.write_text('name = "${FOO}"\n', encoding="utf-8")
    cfg = load_peagen_toml(cfg_file)
    assert cfg["name"] == "bar"
