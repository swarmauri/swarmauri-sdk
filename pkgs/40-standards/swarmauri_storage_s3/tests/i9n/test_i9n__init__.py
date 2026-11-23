import importlib


def test_package_imports():
    module = importlib.import_module("swarmauri_storage_s3")

    assert hasattr(module, "S3StorageAdapter")


def test_all_exports_adapter():
    module = importlib.import_module("swarmauri_storage_s3")

    assert "S3StorageAdapter" in module.__all__
