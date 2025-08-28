from swarmauri_gitfilter_file import FileFilter


def test_roundtrip(tmp_path):
    filt = FileFilter.from_uri(f"file://{tmp_path}")
    oid = filt.clean(b"hello")
    assert filt.smudge(oid) == b"hello"
