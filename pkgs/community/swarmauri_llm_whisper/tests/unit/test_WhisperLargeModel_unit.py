from swarmauri_llm_whisper import WhisperLargeModel


def test_whisperlargemodel_import() -> None:
    assert WhisperLargeModel.__name__ == "WhisperLargeModel"
