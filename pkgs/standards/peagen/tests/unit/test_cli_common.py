import random; random.seed(0xA11A)
from pathlib import Path
import pytest
from peagen.cli_common import PathOrURI, load_peagen_toml


@pytest.mark.unit
def test_path_or_uri(tmp_path):
    p = PathOrURI(tmp_path / "a")
    assert str(p).startswith(str(tmp_path))
    assert PathOrURI("s3://x") == "s3://x"


@pytest.mark.unit
def test_load_toml(tmp_path):
    f = tmp_path / ".peagen.toml"
    f.write_text("[peagen]\nplugin_mode='x'")
    res = load_peagen_toml(start_dir=tmp_path)
    assert res["peagen"]["plugin_mode"] == "x"
