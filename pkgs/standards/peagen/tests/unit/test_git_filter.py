from pathlib import Path
from git import Repo
from peagen._utils.git_filter import add_filter, init_git_filter, DEFAULT_FILTER_URI


def test_add_filter_defaults(tmp_path: Path):
    cfg = tmp_path / ".peagen.toml"
    add_filter(config=cfg)
    text = cfg.read_text()
    assert DEFAULT_FILTER_URI in text


def test_init_git_filter_writes_scripts(tmp_path: Path):
    repo = Repo.init(tmp_path)
    init_git_filter(repo)
    flt_dir = Path(repo.git_dir) / "filters" / "default"
    assert (flt_dir / "clean.py").exists()
    assert (flt_dir / "smudge.py").exists()
