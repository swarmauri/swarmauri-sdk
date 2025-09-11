import io
import pytest

from swarmauri_storage_file import FileStorageAdapter
from peagen.tui.fileops import download_remote, upload_remote


@pytest.mark.unit
def test_remote_file_roundtrip(tmp_path):
    adapter = FileStorageAdapter(tmp_path)
    uri = adapter.upload("foo.txt", io.BytesIO(b"hi"))
    path, adp, key = download_remote(uri)
    assert path.read_text() == "hi"
    path.write_text("bye")
    upload_remote(adp, key, path)
    assert adapter.download(key).read().decode() == "bye"
