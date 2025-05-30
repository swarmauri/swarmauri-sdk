from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_loader import ConfigLoader


def write_sample(tmpdir: Path) -> Path:
    content = """
[workspace]
org = "demo"
workers = 2

[llm]
default_provider = "groq"
default_model_name = "llama"
[llm.groq]
API_KEY = "test"

[storage]
default_storage_adapter = "file"
[storage.adapters.file]
output_dir = "./out"

[publishers]
default_publisher = "redis"
[publishers.adapters.redis]
host = "localhost"
"""
    cfg_path = tmpdir / ".peagen.toml"
    cfg_path.write_text(content)
    return cfg_path


def test_loader_parses_config(tmp_path: Path):
    cfg = write_sample(tmp_path)
    loader = ConfigLoader(path=cfg)
    assert loader.config.workspace.org == "demo"
    assert loader.config.llm.default_provider == "groq"
    assert "groq" in loader.config.llm.providers


def test_loader_singleton(tmp_path: Path):
    cfg = write_sample(tmp_path)
    first = ConfigLoader(path=cfg)
    second = ConfigLoader()
    assert first is second
    assert second.config.workspace.org == "demo"

