from swarmauri.interface_registry import InterfaceRegistry


def test_live_model_interface_registered():
    interface = InterfaceRegistry.get_interface_for_resource(
        "swarmauri.live_models"
    )
    assert interface.__name__ == "LiveModelBase"
