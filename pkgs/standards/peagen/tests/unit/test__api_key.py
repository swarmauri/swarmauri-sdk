import random; random.seed(0xA11A)
import os
import typer
import pytest
from peagen._api_key import _resolve_api_key


@pytest.mark.unit
def test_cli_override():
    assert _resolve_api_key("openai", api_key="k") == "k"


@pytest.mark.unit
def test_env_var(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "envk")
    assert _resolve_api_key("openai") == "envk"


@pytest.mark.unit
def test_toml(monkeypatch, tmp_path):
    toml = tmp_path / ".peagen.toml"
    toml.write_text("[llm.openai]\napi_key='tok'")
    monkeypatch.chdir(tmp_path)
    assert _resolve_api_key("openai") == "tok"


@pytest.mark.unit
def test_missing_provider():
    with pytest.raises(typer.Exit):
        _resolve_api_key("", env_file=None)

