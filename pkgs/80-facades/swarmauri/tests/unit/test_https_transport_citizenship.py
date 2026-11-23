from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_https_unicast_transport_is_first_class() -> None:
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.transports.HttpsUnicastTransport"
        ]
        == "swarmauri_transport_https_unicast.HttpsUnicastTransport"
    )
