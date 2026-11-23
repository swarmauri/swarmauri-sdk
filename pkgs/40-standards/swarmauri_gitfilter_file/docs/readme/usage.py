import tempfile
from pathlib import Path

from swarmauri_gitfilter_file import FileFilter

with tempfile.TemporaryDirectory() as tmpdir:
    uri = Path(tmpdir).as_uri()
    filt = FileFilter.from_uri(uri)
    oid = filt.clean(b"hello")
    assert oid.startswith("sha256:")
    assert filt.smudge(oid) == b"hello"
