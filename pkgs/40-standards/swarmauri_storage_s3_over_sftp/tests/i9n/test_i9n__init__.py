import importlib


def test_package_imports():
    module = importlib.import_module("swarmauri_storage_s3_over_sftp")

    assert hasattr(module, "S3OverSftpStorageAdapter")


def test_all_exports_adapter():
    module = importlib.import_module("swarmauri_storage_s3_over_sftp")

    assert "S3OverSftpStorageAdapter" in module.__all__
