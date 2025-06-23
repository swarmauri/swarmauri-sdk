import pytest

from peagen._utils._source_packages import _copy_tree, _dir_checksum, _sync_dir


@pytest.mark.unit
def test_copy_tree_no_overwrite(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()
    (src / "a.txt").write_text("A", encoding="utf-8")
    (src / "b.txt").write_text("B", encoding="utf-8")
    (dst / "b.txt").write_text("existing", encoding="utf-8")

    _copy_tree(src, dst)
    assert (dst / "a.txt").read_text(encoding="utf-8") == "A"
    # existing file should remain untouched
    assert (dst / "b.txt").read_text(encoding="utf-8") == "existing"


@pytest.mark.unit
def test_dir_checksum_changes(tmp_path):
    root = tmp_path / "data"
    root.mkdir()
    (root / "x.txt").write_text("x")
    first = _dir_checksum(root)
    (root / "x.txt").write_text("y")
    assert _dir_checksum(root) != first


@pytest.mark.unit
def test_sync_dir_uploads(tmp_path):
    root = tmp_path / "up"
    root.mkdir()
    file_path = root / "f.txt"
    file_path.write_text("data")

    class Dummy:
        def __init__(self):
            self.keys = []

        def upload(self, key, fh):
            self.keys.append(key)

    adapter = Dummy()
    _sync_dir(root, adapter, prefix="pre")
    assert adapter.keys == ["pre/f.txt"]
