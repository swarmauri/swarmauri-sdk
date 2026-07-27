from swarmauri.interface_registry import InterfaceRegistry


def test_model_provider_interface_registered():
    interface = InterfaceRegistry.get_interface_for_resource(
        "swarmauri.model_providers"
    )
    assert interface.__name__ == "ModelProviderBase"
