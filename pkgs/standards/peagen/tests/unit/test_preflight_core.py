from pathlib import Path

from peagen.core.preflight_core import ensure_mirror
from peagen.core.mirror_core import ensure_repo, open_repo


def test_ensure_mirror_initialises_repo(tmp_path: Path) -> None:
    origin = tmp_path / "origin.git"
    vcs_origin = ensure_repo(origin)
    (origin / "file.txt").write_text("data", encoding="utf-8")
    vcs_origin.commit(["file.txt"], "init")

    mirror = tmp_path / "mirror"
    ensure_mirror(mirror, str(origin))
    assert (mirror / ".git").exists()
    vcs = open_repo(mirror)
    assert vcs.has_remote()
