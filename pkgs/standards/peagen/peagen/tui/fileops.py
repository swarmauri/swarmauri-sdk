"""Remote file helpers for the Peagen TUI."""

from __future__ import annotations
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from peagen.plugins.git_filters import make_filter_for_uri


def download_remote(uri: str) -> tuple[Path, object, str]:
    """Download *uri* to a temporary file and return (path, adapter, key)."""

    root = uri.rsplit("/", 1)[0] + "/"
    key = uri.rsplit("/", 1)[1]
    adapter = make_filter_for_uri(root)
    data = adapter.download(key)
    tmp = Path(tempfile.mkdtemp()) / Path(urlparse(uri).path).name
    with open(tmp, "wb") as fh:
        fh.write(data.read())
    return tmp, adapter, key


def upload_remote(adapter: object, key: str, path: Path) -> str:
    """Upload *path* using *adapter* under *key* and return the artifact URI."""

    with path.open("rb") as fh:
        return adapter.upload(key, fh)
