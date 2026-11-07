from swarmauri_live_model_gemini import GeminiLiveModel


def test_model_capabilities():
    model = GeminiLiveModel()
    assert "video" in model.capabilities.input_modalities
    assert "audio" in model.capabilities.output_modalities
