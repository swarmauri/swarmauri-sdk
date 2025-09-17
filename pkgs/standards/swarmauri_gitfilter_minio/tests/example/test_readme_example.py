from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest


class _DummyResponse:
    def __init__(self, data: bytes) -> None:
        self._data = data

    def read(self) -> bytes:  # pragma: no cover - trivial accessor
        return self._data

    def close(self) -> None:  # pragma: no cover - interface stub
        pass

    def release_conn(self) -> None:  # pragma: no cover - interface stub
        pass


class _DummyMinio:
    def __init__(
        self, endpoint: str, *, access_key, secret_key, secure
    ) -> None:  # pragma: no cover - simple init
        self._endpoint = endpoint
        self._secure = secure
        self._access_key = access_key
        self._secret_key = secret_key
        self._buckets: set[str] = set()
        self._store: dict[tuple[str, str], bytes] = {}

    def bucket_exists(self, bucket: str) -> bool:
        return bucket in self._buckets

    def make_bucket(self, bucket: str) -> None:
        self._buckets.add(bucket)

    def put_object(self, bucket: str, key: str, data, *, length=-1, part_size=0):
        self._buckets.add(bucket)
        data.seek(0)
        self._store[(bucket, key)] = data.read()

    def get_object(self, bucket: str, key: str):
        return _DummyResponse(self._store[(bucket, key)])

    def list_objects(
        self, bucket: str, *, prefix: str, recursive: bool = False
    ):  # pragma: no cover - unused in test
        for (obj_bucket, obj_key), _ in self._store.items():
            if obj_bucket != bucket:
                continue
            if not obj_key.startswith(prefix):
                continue
            yield type("_Obj", (), {"object_name": obj_key})()


def _extract_first_python_block(readme: Path) -> str:
    content = readme.read_text().splitlines()
    collecting = False
    lines: list[str] = []
    for line in content:
        stripped = line.strip()
        if not collecting and stripped.startswith("```python"):
            collecting = True
            continue
        if collecting and stripped.startswith("```"):
            break
        if collecting:
            lines.append(line)

    if not lines:
        raise AssertionError("README example block is missing")

    return dedent("\n".join(lines))


@pytest.mark.example
def test_readme_usage_example(monkeypatch, tmp_path):
    pkg_root = Path(__file__).resolve().parents[2]
    readme_path = pkg_root / "README.md"
    code = _extract_first_python_block(readme_path)

    monkeypatch.setattr(
        "swarmauri_gitfilter_minio.minio_filter.Minio",
        _DummyMinio,
    )
    monkeypatch.setattr(
        "swarmauri_gitfilter_minio.minio_filter.load_peagen_toml",
        lambda: {
            "storage": {
                "filters": {
                    "minio": {
                        "access_key": "example-access",
                        "secret_key": "example-secret",
                    }
                }
            }
        },
    )

    expected_payload = b"readme contents"
    target_readme = tmp_path / "README.md"
    target_readme.write_bytes(expected_payload)
    monkeypatch.chdir(tmp_path)

    namespace: dict[str, object] = {}
    exec(compile(code, str(readme_path), "exec"), namespace, namespace)

    assert namespace["data"] == expected_payload
    assert namespace["uri"] == "minio://localhost:9000/my-bucket/prefix/docs/README.md"
