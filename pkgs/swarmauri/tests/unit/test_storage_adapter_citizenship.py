from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_s3_storage_adapters_are_first_class():
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.storage_adapters.S3FSStorageAdapter"
        ]
        == "swarmauri_storage_s3fs.S3FSStorageAdapter"
    )
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.storage_adapters.S3StorageAdapter"
        ]
        == "swarmauri_storage_s3.S3StorageAdapter"
    )
