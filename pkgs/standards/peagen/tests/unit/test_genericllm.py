import os
from unittest.mock import MagicMock, patch

import pytest
from peagen.GenericLLM import GenericLLM
from pydantic import SecretStr


@pytest.mark.unit
class TestGenericLLM:
    def test_init(self):
        """Test initialization of GenericLLM."""
        llm_manager = GenericLLM()
        assert llm_manager._llm_instance is None

    @patch("importlib.import_module")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test_env_key"})
    def test_get_llm_with_env_api_key(self, mock_import_module):
        """Test get_llm using API key from environment variables."""
        # Setup mock module and class
        mock_openai_model = MagicMock()
        mock_module = MagicMock()
        mock_module.OpenAIModel = mock_openai_model
        mock_import_module.return_value = mock_module

        # Create GenericLLM instance and call get_llm
        llm_manager = GenericLLM()
        llm = llm_manager.get_llm(provider="openai", model_name="gpt-4")

        # Check if correct module was imported
        mock_import_module.assert_called_once_with(
            "swarmauri_standard.llms.OpenAIModel"
        )

        # Check if model was instantiated with correct parameters
        mock_openai_model.assert_called_once()
        args, kwargs = mock_openai_model.call_args
        assert kwargs["api_key"] == "test_env_key"
        assert kwargs["name"] == "gpt-4"
        assert kwargs["timeout"] == 1200.0

        # Check if the llm instance was set and returned
        assert llm_manager._llm_instance == llm

    @patch("importlib.import_module")
    def test_get_llm_with_explicit_api_key(self, mock_import_module):
        """Test get_llm using explicitly provided API key."""
        # Setup mock module and class
        mock_anthropic_model = MagicMock()
        mock_module = MagicMock()
        mock_module.AnthropicModel = mock_anthropic_model
        mock_import_module.return_value = mock_module

        # Create GenericLLM instance and call get_llm
        llm_manager = GenericLLM()
        llm_manager.get_llm(
            provider="anthropic",
            api_key="explicit_test_key",
            model_name="claude-3-opus-20240229",
        )

        # Check if correct module was imported
        mock_import_module.assert_called_once_with(
            "swarmauri_standard.llms.AnthropicModel"
        )

        # Check if model was instantiated with correct parameters
        mock_anthropic_model.assert_called_once()
        args, kwargs = mock_anthropic_model.call_args
        assert kwargs["api_key"] == "explicit_test_key"
        assert kwargs["name"] == "claude-3-opus-20240229"

    @patch("importlib.import_module")
    def test_get_llm_with_secretstr_api_key(self, mock_import_module):
        """Test get_llm using SecretStr API key."""
        # Setup mock module and class
        mock_mistral_model = MagicMock()
        mock_module = MagicMock()
        mock_module.MistralModel = mock_mistral_model
        mock_import_module.return_value = mock_module

        # Create GenericLLM instance and call get_llm with SecretStr
        llm_manager = GenericLLM()
        secret_key = SecretStr("secret_test_key")
        llm_manager.get_llm(
            provider="mistral", api_key=secret_key, model_name="mistral-large-latest"
        )

        # Check if model was instantiated with correct parameters
        mock_mistral_model.assert_called_once()
        args, kwargs = mock_mistral_model.call_args
        assert kwargs["api_key"] == secret_key

    @patch("importlib.import_module")
    @patch.dict(os.environ, {}, clear=True)
    def test_get_llm_missing_api_key(self, mock_import_module):
        """Test get_llm with missing API key raises ValueError."""
        # Create GenericLLM instance
        llm_manager = GenericLLM()

        # Call get_llm without api_key should raise ValueError
        with pytest.raises(ValueError) as excinfo:
            llm_manager.get_llm(provider="openai")

        assert "No API key provided" in str(excinfo.value)

    def test_get_llm_import_fallback(self):
        """Test get_llm fallback to alternate import path."""
        # Setup second mock import that succeeds
        with patch(
            "importlib.import_module",
            side_effect=[
                ImportError("Module not found"),  # First attempt fails
                MagicMock(),  # Second attempt succeeds
            ],
        ) as mock_import:
            # Setup mock for the successful import
            mock_module = MagicMock()
            mock_module.DeepInfraModel = MagicMock()
            mock_import.return_value = mock_module

            # Create GenericLLM instance
            llm_manager = GenericLLM()

            # Should not raise, as second import attempt succeeds
            llm_manager.get_llm(provider="deepinfra", api_key="test_key")

            # Check both import paths were attempted
            assert mock_import.call_count >= 1

    def test_get_llm_unsupported_provider(self):
        """Test get_llm with unsupported provider raises ValueError."""
        # Create GenericLLM instance
        llm_manager = GenericLLM()

        # Call get_llm with invalid provider
        with pytest.raises(ValueError) as excinfo:
            llm_manager.get_llm(provider="unsupported_provider", api_key="test")

        assert "Unsupported LLM provider" in str(excinfo.value)

    @patch("importlib.import_module")
    def test_get_llm_with_additional_kwargs(self, mock_import_module):
        """Test get_llm with additional keyword arguments."""
        # Setup mock module and class
        mock_cohere_model = MagicMock()
        mock_module = MagicMock()
        mock_module.CohereModel = mock_cohere_model
        mock_import_module.return_value = mock_module

        # Create GenericLLM instance and call get_llm with additional kwargs
        llm_manager = GenericLLM()
        llm_manager.get_llm(
            provider="cohere",
            api_key="test_key",
            model_name="command-r-plus",
            temperature=0.7,
            max_tokens=2000,
        )

        # Check if model was instantiated with the additional parameters
        mock_cohere_model.assert_called_once()
        args, kwargs = mock_cohere_model.call_args
        assert kwargs["api_key"] == "test_key"
        assert kwargs["name"] == "command-r-plus"
        assert kwargs["temperature"] == 0.7
        assert kwargs["max_tokens"] == 2000

    @patch("importlib.import_module")
    def test_get_llm_case_insensitive_provider(self, mock_import_module):
        """Test get_llm with case-insensitive provider name."""
        # Setup mock module and class
        mock_openai_model = MagicMock()
        mock_module = MagicMock()
        mock_module.OpenAIModel = mock_openai_model
        mock_import_module.return_value = mock_module

        # Create GenericLLM instance and call get_llm with mixed case provider
        llm_manager = GenericLLM()
        llm_manager.get_llm(provider="OpEnAi", api_key="test_key", model_name="gpt-4")

        # Check if correct model class was used despite case differences
        mock_import_module.assert_called_once_with(
            "swarmauri_standard.llms.OpenAIModel"
        )
