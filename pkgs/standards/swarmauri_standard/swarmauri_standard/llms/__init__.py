from swarmauri.utils._lazy_import import _lazy_import

# List of llms names (file names without the ".py" extension) and corresponding class names
llms_files = [
    ("swarmauri_standard.llms.AI21StudioModel", "AI21StudioModel"),
    ("swarmauri_standard.llms.AnthropicModel", "AnthropicModel"),
    ("swarmauri_standard.llms.AnthropicToolModel", "AnthropicToolModel"),
    ("swarmauri_standard.llms.BlackForestImgGenModel", "BlackForestImgGenModel"),
    ("swarmauri_standard.llms.CohereModel", "CohereModel"),
    ("swarmauri_standard.llms.CohereToolModel", "CohereToolModel"),
    ("swarmauri_standard.llms.DeepInfraImgGenModel", "DeepInfraImgGenModel"),
    ("swarmauri_standard.llms.DeepInfraModel", "DeepInfraModel"),
    ("swarmauri_standard.llms.DeepSeekModel", "DeepSeekModel"),
    ("swarmauri_standard.llms.FalAIImgGenModel", "FalaiImgGenModel"),
    ("swarmauri_standard.llms.FalAIVisionModel", "FalAIVisionModel"),
    ("swarmauri_standard.llms.GeminiProModel", "GeminiProModel"),
    ("swarmauri_standard.llms.GeminiToolModel", "GeminiToolModel"),
    ("swarmauri_standard.llms.GroqAIAudio", "GroqAIAudio"),
    ("swarmauri_standard.llms.GroqModel", "GroqModel"),
    ("swarmauri_standard.llms.GroqToolModel", "GroqToolModel"),
    ("swarmauri_standard.llms.GroqVisionModel", "GroqVisionModel"),
    ("swarmauri_standard.llms.HyperbolicAudioTTS", "HyperbolicAudioTTS"),
    ("swarmauri_standard.llms.HyperbolicImgGenModel", "HyperbolicImgGenModel"),
    ("swarmauri_standard.llms.HyperbolicModel", "HyperbolicModel"),
    ("swarmauri_standard.llms.HyperbolicVisionModel", "HyperbolicVisionModel"),
    ("swarmauri_standard.llms.MistralModel", "MistralModel"),
    ("swarmauri_standard.llms.MistralToolModel", "MistralToolModel"),
    ("swarmauri_standard.llms.OpenAIAudio", "OpenAIAudio"),
    ("swarmauri_standard.llms.OpenAIAudioTTS", "OpenAIAudioTTS"),
    ("swarmauri_standard.llms.OpenAIImgGenModel", "OpenAIImgGenModel"),
    ("swarmauri_standard.llms.OpenAIModel", "OpenAIModel"),
    ("swarmauri_standard.llms.OpenAIToolModel", "OpenAIToolModel"),
    ("swarmauri_standard.llms.PerplexityModel", "PerplexityModel"),
    ("swarmauri_standard.llms.PlayHTModel", "PlayHTModel"),
    ("swarmauri_standard.llms.WhisperLargeModel", "WhisperLargeModel"),
]

# Lazy loading of llms classes, storing them in variables
for module_name, class_name in llms_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded llms classes to __all__
__all__ = [class_name for _, class_name in llms_files]
