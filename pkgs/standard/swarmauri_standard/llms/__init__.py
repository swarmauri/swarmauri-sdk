from swarmauri.utils._lazy_import import _lazy_import

# List of llms names (file names without the ".py" extension) and corresponding class names
llms_files = [
    ("swarmauri.llms.concrete.AI21StudioModel", "AI21StudioModel"),
    ("swarmauri.llms.concrete.AnthropicModel", "AnthropicModel"),
    ("swarmauri.llms.concrete.AnthropicToolModel", "AnthropicToolModel"),
    ("swarmauri.llms.concrete.BlackForestImgGenModel", "BlackForestImgGenModel"),
    ("swarmauri.llms.concrete.CohereModel", "CohereModel"),
    ("swarmauri.llms.concrete.CohereToolModel", "CohereToolModel"),
    ("swarmauri.llms.concrete.DeepInfraImgGenModel", "DeepInfraImgGenModel"),
    ("swarmauri.llms.concrete.DeepInfraModel", "DeepInfraModel"),
    ("swarmauri.llms.concrete.DeepSeekModel", "DeepSeekModel"),
    ("swarmauri.llms.concrete.FalAIImgGenModel", "FalaiImgGenModel"),
    ("swarmauri.llms.concrete.FalAIVisionModel", "FalAIVisionModel"),
    ("swarmauri.llms.concrete.GeminiProModel", "GeminiProModel"),
    ("swarmauri.llms.concrete.GeminiToolModel", "GeminiToolModel"),
    ("swarmauri.llms.concrete.GroqAIAudio", "GroqAIAudio"),
    ("swarmauri.llms.concrete.GroqModel", "GroqModel"),
    ("swarmauri.llms.concrete.GroqToolModel", "GroqToolModel"),
    ("swarmauri.llms.concrete.GroqVisionModel", "GroqVisionModel"),
    ("swarmauri.llms.concrete.HyperbolicAudioTTS", "HyperbolicAudioTTS"),
    ("swarmauri.llms.concrete.HyperbolicImgGenModel", "HyperbolicImgGenModel"),
    ("swarmauri.llms.concrete.HyperbolicModel", "HyperbolicModel"),
    ("swarmauri.llms.concrete.HyperbolicVisionModel", "HyperbolicVisionModel"),
    ("swarmauri.llms.concrete.MistralModel", "MistralModel"),
    ("swarmauri.llms.concrete.MistralToolModel", "MistralToolModel"),
    ("swarmauri.llms.concrete.OpenAIAudio", "OpenAIAudio"),
    ("swarmauri.llms.concrete.OpenAIAudioTTS", "OpenAIAudioTTS"),
    ("swarmauri.llms.concrete.OpenAIImgGenModel", "OpenAIImgGenModel"),
    ("swarmauri.llms.concrete.OpenAIModel", "OpenAIModel"),
    ("swarmauri.llms.concrete.OpenAIToolModel", "OpenAIToolModel"),
    ("swarmauri.llms.concrete.PerplexityModel", "PerplexityModel"),
    ("swarmauri.llms.concrete.PlayHTModel", "PlayHTModel"),
    ("swarmauri.llms.concrete.WhisperLargeModel", "WhisperLargeModel"),
]

# Lazy loading of llms classes, storing them in variables
for module_name, class_name in llms_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded llms classes to __all__
__all__ = [class_name for _, class_name in llms_files]
