from importlib.metadata import entry_points, version
from typing import ClassVar, Literal

import pytest

from swarmauri_agent_texttospeech import TextToSpeechAgent, __version__
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.tts.TTSBase import TTSBase


pytestmark = pytest.mark.unit


@ComponentBase.register_type(TTSBase, "StubTTS")
class StubTTS(TTSBase):
    allowed_models: list[str] = ["test"]
    name: str = "test"
    calls: ClassVar[list[tuple[str, str]]] = []
    type: Literal["StubTTS"] = "StubTTS"

    def predict(self, text: str, audio_path: str = "output.mp3") -> str:
        self.calls.append((text, audio_path))
        return audio_path

    async def apredict(self, text: str, audio_path: str = "output.mp3") -> str:
        self.calls.append((text, audio_path))
        return audio_path

    def stream(self, text: str, **kwargs):
        yield text.encode()

    async def astream(self, text: str, **kwargs):
        yield text.encode()

    def batch(self, text_path_dict):
        return [
            self.predict(text, path) for text, path in text_path_dict.items()
        ]

    async def abatch(self, text_path_dict, max_concurrent: int = 5):
        return [
            await self.apredict(text, path)
            for text, path in text_path_dict.items()
        ]


@pytest.fixture(autouse=True)
def clear_calls() -> None:
    StubTTS.calls.clear()


@pytest.fixture
def agent() -> TextToSpeechAgent:
    return TextToSpeechAgent(tts=StubTTS(), output_path="speech.mp3")


def test_agent_metadata_and_registration(agent: TextToSpeechAgent) -> None:
    assert isinstance(agent, AgentBase)
    assert agent.resource == "Agent"
    assert agent.type == "TextToSpeechAgent"
    assert agent.llm is None
    assert not hasattr(agent, "conversation")
    assert not hasattr(agent, "system_context")


def test_exec_is_stateless(agent: TextToSpeechAgent) -> None:
    assert agent.exec(" First prompt ") == "speech.mp3"
    assert agent.exec("Second prompt", audio_path="second.mp3") == "second.mp3"
    assert StubTTS.calls == [
        ("First prompt", "speech.mp3"),
        ("Second prompt", "second.mp3"),
    ]


@pytest.mark.asyncio
async def test_aexec(agent: TextToSpeechAgent) -> None:
    assert await agent.aexec("Async prompt") == "speech.mp3"
    assert StubTTS.calls == [("Async prompt", "speech.mp3")]


def test_batch_uses_distinct_paths(agent: TextToSpeechAgent) -> None:
    assert agent.batch(["One", "Two"]) == ["speech_0.mp3", "speech_1.mp3"]


def test_empty_input_is_rejected(agent: TextToSpeechAgent) -> None:
    with pytest.raises(ValueError, match="cannot be empty"):
        agent.exec("  ")


def test_serialization(agent: TextToSpeechAgent) -> None:
    restored = TextToSpeechAgent.model_validate_json(agent.model_dump_json())

    assert restored.type == agent.type
    assert restored.tts.type == "StubTTS"


def test_package_version() -> None:
    assert __version__ == version("swarmauri_agent_texttospeech")


def test_agent_entry_point() -> None:
    agents = entry_points(group="swarmauri.agents")
    entry_point = next(
        item for item in agents if item.name == "TextToSpeechAgent"
    )

    assert (
        entry_point.value == "swarmauri_agent_texttospeech:TextToSpeechAgent"
    )
