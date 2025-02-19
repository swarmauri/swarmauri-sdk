# # swarmauri_standard/llms/__init__.py

# from typing import TYPE_CHECKING

# from swarmauri_standard.utils.LazyLoader import LazyLoader  # Ensure correct import path

# # List of LLMs (Large Language Models) names (module paths) and corresponding class names
# llms_files = [
#     ("swarmauri_standard.llms.AI21StudioModel", "AI21StudioModel"),
#     ("swarmauri_standard.llms.AnthropicModel", "AnthropicModel"),
#     ("swarmauri_standard.llms.AnthropicToolModel", "AnthropicToolModel"),
#     ("swarmauri_standard.llms.BlackForestImgGenModel", "BlackForestImgGenModel"),
#     ("swarmauri_standard.llms.CohereModel", "CohereModel"),
#     ("swarmauri_standard.llms.CohereToolModel", "CohereToolModel"),
#     ("swarmauri_standard.llms.DeepInfraImgGenModel", "DeepInfraImgGenModel"),
#     ("swarmauri_standard.llms.DeepInfraModel", "DeepInfraModel"),
#     ("swarmauri_standard.llms.DeepSeekModel", "DeepSeekModel"),
#     ("swarmauri_standard.llms.FalAIImgGenModel", "FalaiImgGenModel"),
#     ("swarmauri_standard.llms.FalAIVisionModel", "FalAIVisionModel"),
#     ("swarmauri_standard.llms.GeminiProModel", "GeminiProModel"),
#     ("swarmauri_standard.llms.GeminiToolModel", "GeminiToolModel"),
#     ("swarmauri_standard.llms.GroqAIAudio", "GroqAIAudio"),
#     ("swarmauri_standard.llms.GroqModel", "GroqModel"),
#     ("swarmauri_standard.llms.GroqToolModel", "GroqToolModel"),
#     ("swarmauri_standard.llms.GroqVisionModel", "GroqVisionModel"),
#     ("swarmauri_standard.llms.HyperbolicAudioTTS", "HyperbolicAudioTTS"),
#     ("swarmauri_standard.llms.HyperbolicImgGenModel", "HyperbolicImgGenModel"),
#     ("swarmauri_standard.llms.HyperbolicModel", "HyperbolicModel"),
#     ("swarmauri_standard.llms.HyperbolicVisionModel", "HyperbolicVisionModel"),
#     ("swarmauri_standard.llms.MistralModel", "MistralModel"),
#     ("swarmauri_standard.llms.MistralToolModel", "MistralToolModel"),
#     ("swarmauri_standard.llms.OpenAIAudio", "OpenAIAudio"),
#     ("swarmauri_standard.llms.OpenAIAudioTTS", "OpenAIAudioTTS"),
#     ("swarmauri_standard.llms.OpenAIImgGenModel", "OpenAIImgGenModel"),
#     ("swarmauri_standard.llms.OpenAIModel", "OpenAIModel"),
#     ("swarmauri_standard.llms.OpenAIToolModel", "OpenAIToolModel"),
#     ("swarmauri_standard.llms.PerplexityModel", "PerplexityModel"),
#     ("swarmauri_standard.llms.PlayHTModel", "PlayHTModel"),
#     ("swarmauri_standard.llms.WhisperLargeModel", "WhisperLargeModel"),
# ]

# # Initialize LazyLoader instances for each LLM class
# for module_path, class_name in llms_files:
#     globals()[class_name] = LazyLoader(module_path, class_name)

# # Define __all__ to include all lazy-loaded classes
# __all__ = [class_name for _, class_name in llms_files]

# # Type hinting for static analysis and IDE support
# if TYPE_CHECKING:
#     from swarmauri_standard.llms.AI21StudioModel import AI21StudioModel
#     from swarmauri_standard.llms.AnthropicModel import AnthropicModel
#     from swarmauri_standard.llms.AnthropicToolModel import AnthropicToolModel
#     from swarmauri_standard.llms.BlackForestImgGenModel import BlackForestImgGenModel
#     from swarmauri_standard.llms.CohereModel import CohereModel
#     from swarmauri_standard.llms.CohereToolModel import CohereToolModel
#     from swarmauri_standard.llms.DeepInfraImgGenModel import DeepInfraImgGenModel
#     from swarmauri_standard.llms.DeepInfraModel import DeepInfraModel
#     from swarmauri_standard.llms.DeepSeekModel import DeepSeekModel
#     from swarmauri_standard.llms.FalAIImgGenModel import FalaiImgGenModel
#     from swarmauri_standard.llms.FalAIVisionModel import FalAIVisionModel
#     from swarmauri_standard.llms.GeminiProModel import GeminiProModel
#     from swarmauri_standard.llms.GeminiToolModel import GeminiToolModel
#     from swarmauri_standard.llms.GroqAIAudio import GroqAIAudio
#     from swarmauri_standard.llms.GroqModel import GroqModel
#     from swarmauri_standard.llms.GroqToolModel import GroqToolModel
#     from swarmauri_standard.llms.GroqVisionModel import GroqVisionModel
#     from swarmauri_standard.llms.HyperbolicAudioTTS import HyperbolicAudioTTS
#     from swarmauri_standard.llms.HyperbolicImgGenModel import HyperbolicImgGenModel
#     from swarmauri_standard.llms.HyperbolicModel import HyperbolicModel
#     from swarmauri_standard.llms.HyperbolicVisionModel import HyperbolicVisionModel
#     from swarmauri_standard.llms.MistralModel import MistralModel
#     from swarmauri_standard.llms.MistralToolModel import MistralToolModel
#     from swarmauri_standard.llms.OpenAIAudio import OpenAIAudio
#     from swarmauri_standard.llms.OpenAIAudioTTS import OpenAIAudioTTS
#     from swarmauri_standard.llms.OpenAIImgGenModel import OpenAIImgGenModel
#     from swarmauri_standard.llms.OpenAIModel import OpenAIModel
#     from swarmauri_standard.llms.OpenAIToolModel import OpenAIToolModel
#     from swarmauri_standard.llms.PerplexityModel import PerplexityModel
#     from swarmauri_standard.llms.PlayHTModel import PlayHTModel
#     from swarmauri_standard.llms.WhisperLargeModel import WhisperLargeModel
