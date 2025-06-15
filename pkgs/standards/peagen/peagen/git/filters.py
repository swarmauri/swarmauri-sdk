from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from peagen.plugins.storage_adapters import make_adapter_for_uri


def _get_adapter() -> Any:
    uri = os.environ.get("PEAGEN_S3_URI") or os.environ.get("PEAGEN_ARTIFACTS_URI")
    if not uri:
        raise RuntimeError("PEAGEN_S3_URI environment variable not set")
    return make_adapter_for_uri(uri)


def _object_exists(adapter: Any, key: str) -> bool:
    client = getattr(adapter, "_client", None)
    bucket = getattr(adapter, "_bucket", None)
    if client and bucket:
        try:  # type: ignore[attr-defined]
            client.stat_object(bucket, adapter._full_key(key))  # type: ignore[attr-defined]
            return True
        except Exception:
            return False
    return False


def s3_clean_main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: s3_clean <file>")
    s3_clean(sys.argv[1])


def s3_clean(path: str) -> None:
    file_path = Path(path)
    data = file_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    key = f"artefacts/{digest[:2]}/{digest}{file_path.suffix}"
    adapter = _get_adapter()
    if not _object_exists(adapter, key):
        adapter.upload(key, io.BytesIO(data))
    pointer = {"s3": f"{adapter.root_uri}{key}", "sha256": digest}
    sys.stdout.write(json.dumps(pointer))


def s3_smudge_main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: s3_smudge <file>")
    s3_smudge(sys.argv[1])


def s3_smudge(path: str) -> None:
    pointer = json.load(sys.stdin)
    uri = pointer.get("s3")
    if not uri:
        sys.stdout.write(json.dumps(pointer))
        return
    key = uri.rsplit("/", 1)[1]
    adapter = make_adapter_for_uri(uri.rsplit("/", 1)[0] + "/")
    data = adapter.download(key)
    sys.stdout.buffer.write(data.read())


def setup_s3fs_filters(repo: str | Path = ".", name: str = "s3fs") -> None:
    repo_path = Path(repo)
    subprocess.check_call([
        "git",
        "config",
        "--local",
        f"filter.{name}.clean",
        "peagen-s3-clean %f",
    ], cwd=repo_path)
    subprocess.check_call([
        "git",
        "config",
        "--local",
        f"filter.{name}.smudge",
        "peagen-s3-smudge %f",
    ], cwd=repo_path)
    subprocess.check_call([
        "git",
        "config",
        "--local",
        f"filter.{name}.required",
        "true",
    ], cwd=repo_path)
