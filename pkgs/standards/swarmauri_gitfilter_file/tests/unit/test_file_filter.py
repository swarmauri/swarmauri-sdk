import hashlib
import os
from importlib import import_module
from types import SimpleNamespace

import pytest
from swarmauri_storage_file import FileStorageAdapter

from swarmauri_gitfilter_file import FileFilter


def test_clean_smudge(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    oid = filt.clean(b"data")
    assert filt.smudge(oid) == b"data"


def test_resource_type(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    assert filt.resource == "StorageAdapter"
    assert filt.type == "FileFilter"


def test_round_trip_serialization(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    data = filt.model_dump()
    restored = FileFilter(output_dir=tmp_path, **data)
    assert restored.type == filt.type


@pytest.fixture
def legacy_object(tmp_path, monkeypatch):
    """Exercise legacy reads on Windows without creating an NTFS ADS."""
    payload = b"legacy content"
    oid = "sha256:" + hashlib.sha256(payload).hexdigest()
    if os.name == "nt":
        legacy = tmp_path / "legacy-object"
        original = FileStorageAdapter._full_key

        def full_key(adapter, key, *, allow_empty=True):
            if key == oid:
                return legacy
            return original(adapter, key, allow_empty=allow_empty)

        monkeypatch.setattr(FileStorageAdapter, "_full_key", full_key)
        module = import_module("swarmauri_gitfilter_file.file_filter")
        monkeypatch.setattr(
            module, "os", SimpleNamespace(name="posix"), raising=False
        )
    else:
        legacy = tmp_path / oid
    legacy.write_bytes(payload)
    return FileFilter(output_dir=tmp_path), oid, payload, legacy


def test_legacy_object_is_read_without_copying(legacy_object):
    filt, oid, payload, legacy = legacy_object
    assert filt.smudge(oid) == payload
    assert filt.clean(payload) == oid
    assert legacy.read_bytes() == payload
    assert not filt._full_key(oid).exists()


def test_portable_object_takes_precedence(legacy_object):
    filt, oid, payload, legacy = legacy_object
    portable = filt._full_key(oid)
    portable.parent.mkdir(parents=True)
    portable.write_bytes(b"portable copy")
    assert filt.smudge(oid) == b"portable copy"
    assert legacy.read_bytes() == payload


def test_missing_legacy_and_portable_object_raises(legacy_object):
    filt, oid, _, legacy = legacy_object
    legacy.unlink()
    with pytest.raises(FileNotFoundError):
        filt.smudge(oid)


def test_new_object_uses_portable_layout(tmp_path):
    filt = FileFilter(output_dir=tmp_path)
    oid = filt.clean(b"new content")
    assert (
        tmp_path / "sha256" / oid.split(":", 1)[1]
    ).read_bytes() == b"new content"


@pytest.mark.skipif(
    os.name == "nt", reason="NTFS colon names are alternate data streams"
)
def test_legacy_read_preserves_storage_prefix(tmp_path):
    root = tmp_path / "prefix"
    root.mkdir()
    oid = "sha256:" + hashlib.sha256(b"prefixed").hexdigest()
    (root / oid).write_bytes(b"prefixed")
    assert (
        FileFilter(output_dir=tmp_path, prefix="prefix").smudge(oid)
        == b"prefixed"
    )
