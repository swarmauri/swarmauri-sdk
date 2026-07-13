import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


pytestmark = pytest.mark.unit


def test_playht_model_is_first_class_tts() -> None:
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY[
            "swarmauri.tts.PlayHTModel"
        ]
        == "swarmauri_tts_playht.PlayHTModel"
    )


def test_playht_model_is_not_registered_as_an_llm() -> None:
    assert (
        "swarmauri.llms.PlayHTModel"
        not in PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY
    )
    assert (
        "swarmauri.llms.PlayHTModel"
        not in PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    )
