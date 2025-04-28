"""
GenericLLM.py

This module provides a generic interface to all LLM providers available in swarmauri_standard.
It dynamically loads and instantiates LLM classes based on the specified provider.
"""

import importlib
import os
from typing import Optional, Union

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
    - and more...
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
    }

    def __init__(self):
        self._llm_instance = None

    def get_llm(
        self,
        provider: str,
        api_key: Optional[Union[str, SecretStr]] = None,
        model_name: Optional[str] = None,
        timeout: int = 1200.0,
        **kwargs,
    ) -> LLMBase:
        """
        Creates and returns an instance of the specified LLM provider.

        Args:
            provider: The name of the LLM provider (e.g., 'openai', 'anthropic', 'deepinfra')
            api_key: API key for the provider
            model_name: The specific model to use
            use_tools: Whether to use the tool-enabled version of the model (if available)
            timeout: Request timeout in seconds
            **kwargs: Additional arguments to pass to the LLM constructor

        Returns:
            An instance of the requested LLM

        Raises:
            ValueError: If the provider is not supported or other initialization issues
        """

        provider = provider.lower()

        if provider in self._providers:
            class_name = self._providers[provider]
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported providers: {list(self._providers.keys())}"
            )

        # Get API key from environment if not provided
        if api_key is None:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.environ.get(env_var)
            print(f"API key: {api_key}")
            if api_key is None:
                raise ValueError(
                    f"No API key provided for {provider}. "
                    f"Please provide an API key or set the {env_var} environment variable."
                )

        # Try to import from both standard package paths
        try:
            # First try from swarmauri_standard.llms
            module = importlib.import_module(f"swarmauri_standard.llms.{class_name}")
        except ImportError:
            try:
                # Then try from swarmauri.llms (which might be an alias)
                module = importlib.import_module(f"swarmauri.llms.{class_name}")

            except ImportError:
                raise ImportError(
                    f"Could not import {class_name} from any known module path"
                )

        # Get the class and instantiate it
        llm_class = getattr(module, class_name)

        # Prepare initialization arguments
        init_args = {"timeout": timeout, **kwargs}

        # Add model name if provided
        if model_name:
            init_args["name"] = model_name

        # Add API key if provided
        if api_key:
            init_args["api_key"] = api_key

        # Create the LLM instance
        self._llm_instance = llm_class(**init_args)
        return self._llm_instance
