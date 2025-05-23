"""Generic interface to swarmauri-standard LLM providers.

The module dynamically loads and instantiates provider-specific classes
based on configuration or CLI options.
"""

import importlib
import os
from pathlib import Path
from typing import Optional, Union

import tomllib
from pydantic import SecretStr
from swarmauri_base.llms.LLMBase import LLMBase


class GenericLLM:
    """
    A generic class that provides a unified interface to all supported LLM providers.
    It dynamically loads and instantiates the appropriate LLM class based on the specified provider.

    Supported providers include:
    - OpenAI/O1 (o1, openai)
    - Anthropic (anthropic)
    - Cohere (cohere)
    - DeepInfra (deepinfra)
    - LlamaCpp (llamacpp)
    - Groq (groq)
    - Gemini/Google (gemini, google)
    - Mistral (mistral)
    - DeepSeek (deepseek)
    - AI21Studio (ai21studio)
    - Hyperbolic (hyperbolic)
    - Cerebras (cerebras)
    """

    _providers = {
        "o1": "O1Model",
        "openai": "OpenAIModel",
        "anthropic": "AnthropicModel",
        "cohere": "CohereModel",
        "deepinfra": "DeepInfraModel",
        "llamacpp": "LlamaCppModel",
        "groq": "GroqModel",
        "gemini": "GeminiProModel",
        "google": "GeminiProModel",
        "mistral": "MistralModel",
        "deepseek": "DeepSeekModel",
        "ai21studio": "AI21StudioModel",
        "hyperbolic": "HyperbolicModel",
        "cerebras": "CerebrasModel",
    }

    def __init__(self):
        self._llm_instance = None

    def get_llm(
        self,
        provider: str,
        api_key: Optional[Union[str, SecretStr]] = None,
        model_name: Optional[str] = None,
        timeout: Union[int, float] = 1200.0,
        **kwargs,
    ) -> LLMBase:
        """
        Creates and returns an instance of the specified LLM provider.

        Args:
            provider: The name of the LLM provider (e.g., 'openai', 'anthropic', 'deepinfra')
            api_key: API key for the provider
            model_name: The specific model to use
            timeout: Request timeout in seconds
            **kwargs: Additional arguments to pass to the LLM constructor

        Returns:
            An instance of the requested LLM

        Raises:
            ValueError: If the provider is not supported or no API key is found
            ImportError: If the provider module cannot be imported
        """

        provider = provider.lower()
        if provider in self._providers:
            class_name = self._providers[provider]
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: {list(self._providers.keys())}"
            )

        # 1️⃣ CLI-provided api_key stays
        # 2️⃣ Try .peagen.toml for provider-specific API key
        if api_key is None:
            toml_path = None
            for folder in [Path.cwd(), *Path.cwd().parents]:
                candidate = folder / ".peagen.toml"
                if candidate.is_file():
                    toml_path = candidate
                    break
            if toml_path:
                try:
                    with toml_path.open("rb") as f:
                        toml_data = tomllib.load(f)
                    llm_section = toml_data.get("llm", {})
                    provider_section = llm_section.get(provider, {}) or llm_section.get(
                        provider.lower(), {}
                    )
                    toml_api_key = provider_section.get(
                        "API_KEY"
                    ) or provider_section.get("api_key")
                    if toml_api_key:
                        api_key = toml_api_key
                except Exception:
                    pass

        # 3️⃣ Fallback to environment variable
        if api_key is None:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var)

        # 4️⃣ Error if no API key found
        if api_key is None:
            raise ValueError(
                f"No API key provided for {provider}. "
                f"Please provide it via --api-key, .peagen.toml [llm.{provider}].API_KEY, or set the {env_var} environment variable."
            )

        # Dynamically import provider module
        try:
            module = importlib.import_module(f"swarmauri_standard.llms.{class_name}")
        except ImportError:
            try:
                module = importlib.import_module(f"swarmauri.llms.{class_name}")
            except ImportError:
                raise ImportError(
                    f"Could not import {class_name} from any known module path"
                )

        llm_class = getattr(module, class_name)

        # Prepare initialization arguments
        init_args = {"timeout": timeout, **kwargs}
        if model_name:
            init_args["name"] = model_name
        if api_key:
            init_args["api_key"] = api_key

        # Create and return the LLM instance
        self._llm_instance = llm_class(**init_args)
        return self._llm_instance
