def test_package_importable() -> None:
    from swarmauri_storage_webdav import WebDAVStorageAdapter

    assert WebDAVStorageAdapter.__name__ == "WebDAVStorageAdapter"
