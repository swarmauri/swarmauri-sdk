import pytest

from swarmauri_base.storage import StorageAdapterBase


@pytest.fixture
def adapter() -> StorageAdapterBase:
    return StorageAdapterBase()


@pytest.mark.parametrize(
    "key", ["../escape.txt", "safe/../escape.txt", r"safe\escape.txt"]
)
def test_normalize_key_rejects_traversal_keys(
    adapter: StorageAdapterBase, key: str
) -> None:
    with pytest.raises(ValueError, match="unsafe storage key"):
        adapter.normalize_key(key)


def test_download_target_for_key_resolves_inside_destination(
    adapter: StorageAdapterBase, tmp_path
) -> None:
    assert (
        adapter.download_target_for_key(tmp_path, "safe/file.txt")
        == tmp_path / "safe" / "file.txt"
    )


def test_download_target_for_key_rejects_escape(
    adapter: StorageAdapterBase, tmp_path
) -> None:
    with pytest.raises(ValueError, match="unsafe storage key"):
        adapter.download_target_for_key(tmp_path, "../escape.txt")


def test_storage_path_for_key_resolves_inside_root(
    adapter: StorageAdapterBase, tmp_path
) -> None:
    assert (
        adapter.storage_path_for_key(tmp_path, "safe/file.txt")
        == tmp_path / "safe" / "file.txt"
    )
