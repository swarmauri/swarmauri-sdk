"""Ensure README examples stay in sync with the implementation."""

from __future__ import annotations

import re
from pathlib import Path

import pytest


class _DummyObject:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data

    def close(self) -> None:  # pragma: no cover - compatibility shim
        pass

    def release_conn(self) -> None:  # pragma: no cover - compatibility shim
        pass


class _DummyClient:
    def __init__(self, *args, **kwargs):
        self.objects: dict[str, bytes] = {}

    def bucket_exists(self, bucket: str) -> bool:
        return True

    def make_bucket(self, bucket: str) -> None:  # pragma: no cover - never called
        pass

    def put_object(self, bucket: str, key: str, data, *, length: int, part_size: int):
        self.objects[key] = data.read()

    def get_object(self, bucket: str, key: str) -> _DummyObject:
        return _DummyObject(self.objects[key])


@pytest.mark.example
def test_usage_example_executes(monkeypatch, capsys):
    """Run the README usage example with a stubbed MinIO client."""

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    content = readme_path.read_text(encoding="utf-8")
    match = re.search(r"```python\n(.*?)```", content, re.DOTALL)
    assert match, "Could not find a python code block in the README"
    code = match.group(1)
    assert "MinioStorageAdapter" in code, "Unexpected python example selected"

    import swarmauri_storage_minio.minio_storage_adapter as adapter_module

    monkeypatch.setattr(adapter_module, "Minio", _DummyClient)

    namespace: dict[str, object] = {}
    exec(compile(code, str(readme_path), "exec"), namespace)

    captured = capsys.readouterr().out.strip().splitlines()
    assert captured, "The example did not produce any output"
    assert len(captured) >= 2, f"Unexpected output: {captured!r}"
    assert captured[0].endswith("artifact.txt"), captured[0]
    assert captured[1] == "data", captured

    assert namespace["uri"].endswith("artifact.txt")  # type: ignore[index]
    assert namespace["downloaded"] == b"data"  # type: ignore[index]
