import importlib

# Define a lazy loader function with a warning message if the module is not found
def _lazy_import(module_name, module_description=None):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        # If module is not available, print a warning message
        print(f"Warning: The module '{module_description or module_name}' is not available. "
              f"Please install the necessary dependencies to enable this functionality.")
        return None

# List of model names (file names without the ".py" extension)
model_files = [
    "AI21StudioModel",
    "AnthropicModel",
    "AnthropicToolModel",
    "BlackForestimgGenModel",
    "CohereModel",
    "CohereToolModel",
    "DeepInfraImgGenModel",
    "DeepInfraModel",
    "DeepSeekModel",
    "FalAllImgGenModel",
    "FalAVisionModel",
    "GeminiProModel",
    "GeminiToolModel",
    "GroqAudio",
    "GroqModel",
    "GroqToolModel",
    "GroqVisionModel",
    "MistralModel",
    "MistralToolModel",
    "OpenAIGenModel",
    "OpenAIModel",
    "OpenAIToolModel",
    "PerplexityModel",
    "PlayHTModel",
    "WhisperLargeModel",
]

# Lazy loading of models, storing them in variables
for model in model_files:
    globals()[model] = _lazy_import(f"swarmauri.llms.concrete.{model}", model)

# Adding the lazy-loaded models to __all__
__all__ = model_files
