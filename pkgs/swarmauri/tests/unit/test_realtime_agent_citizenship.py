from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_realtime_agent_citizenship():
    assert (
        PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY[
            "swarmauri.agents.RealtimeAgent"
        ]
        == "swarmauri_agent_realtime.RealtimeAgent"
    )
