import pytest
from pathlib import Path

from peagen.config_loader import TomlConfigLoader


@pytest.mark.unit
def test_load_from_explicit_path(tmp_path: Path):
    cfg = tmp_path / ".peagen.toml"
    cfg.write_text("foo = 'bar'", encoding="utf-8")
    loader = TomlConfigLoader(path=cfg)
    assert loader.path == cfg
    assert loader.get("foo") == "bar"


@pytest.mark.unit
def test_discover_from_start_dir(tmp_path: Path):
    cfg = tmp_path / ".peagen.toml"
    cfg.write_text("x = 1", encoding="utf-8")
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    loader = TomlConfigLoader(start_dir=nested)
    assert loader.path == cfg
    assert loader.get("x") == 1


@pytest.mark.unit
def test_jinja_env_secrets(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("OPENAI_KEY=abc", encoding="utf-8")
    cfg = tmp_path / ".peagen.toml"
    cfg.write_text("llm_api_key = \"{{ secrets.OPENAI_KEY }}\"", encoding="utf-8")
    loader = TomlConfigLoader(path=cfg)
    assert loader.get("llm_api_key") == "abc"


@pytest.mark.unit
def test_nested_env_keys(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("llm.api_keys.openai=xyz", encoding="utf-8")
    cfg = tmp_path / ".peagen.toml"
    cfg.write_text(
        """
        [llm.api_keys]
        openai = "{{ secrets.llm.api_keys.openai }}"
        """,
        encoding="utf-8",
    )
    loader = TomlConfigLoader(path=cfg)
    assert loader.get("llm")["api_keys"]["openai"] == "xyz"


