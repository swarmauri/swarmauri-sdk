from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_retrying_http_client_is_first_class_transport():
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.transports.RetryingHttpClient"
        ]
        == "swarmauri_transport_retry.RetryingHttpClient"
    )
