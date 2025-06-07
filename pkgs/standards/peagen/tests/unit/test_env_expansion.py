import os
from pathlib import Path
from peagen._utils.config_loader import load_peagen_toml
from pydantic import SecretStr

def test_env_variable_expansion(tmp_path, monkeypatch):
    cfg_file = tmp_path / ".peagen.toml"
    cfg_file.write_text('token = "${MY_SECRET}"\n', encoding="utf-8")
    monkeypatch.setenv("MY_SECRET", "hidden")
    cfg = load_peagen_toml(cfg_file)
    assert isinstance(cfg["token"], SecretStr)
    assert cfg["token"].get_secret_value() == "hidden"
    assert "hidden" not in repr(cfg["token"])
