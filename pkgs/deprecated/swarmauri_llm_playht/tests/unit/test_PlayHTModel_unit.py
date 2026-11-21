from swarmauri_llm_playht import PlayHTModel
from swarmauri_base.tts.TTSBase import TTSBase


def test_playhtmodel_import() -> None:
    assert PlayHTModel.__name__ == "PlayHTModel"
    assert issubclass(PlayHTModel, TTSBase)
