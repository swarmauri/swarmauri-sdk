from swarmauri_core.storage.IStorageAdapter import IStorageAdapter


def test_storage_adapter_interface_methods():
    abstract_methods = IStorageAdapter.__abstractmethods__
    expected = {
        "upload",
        "download",
        "get_blob",
        "put_blob",
        "upload_dir",
        "push",
        "download_dir",
        "pull",
        "from_uri",
    }
    assert expected.issubset(abstract_methods)
