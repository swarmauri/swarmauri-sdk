import importlib


def test_package_imports():
    module = importlib.import_module("swarmauri_storage_s3fs")

    assert hasattr(module, "S3FSStorageAdapter")


def test_all_exports_adapter():
    module = importlib.import_module("swarmauri_storage_s3fs")

    assert "S3FSStorageAdapter" in module.__all__
