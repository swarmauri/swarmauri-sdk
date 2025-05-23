import os
from unittest.mock import patch

import pytest
import typer
from peagen._api_key import _resolve_api_key


@pytest.mark.r8n
class TestApiKey:
    def test_explicit_api_key(self):
        """Test that explicitly provided API key is returned as-is"""
        result = _resolve_api_key("openai", api_key="test-key-123")
        assert result == "test-key-123"

    def test_missing_provider(self):
        """Test that function raises error when provider is not provided"""
        with pytest.raises(typer.Exit) as excinfo:
            _resolve_api_key(provider=None)
        assert excinfo.value.exit_code == 1

    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-key-456"}, clear=True)
    def test_environment_variable_lookup(self):
        """Test that function finds API key from environment variable"""
        result = _resolve_api_key("openai")
        assert result == "env-key-456"

    @patch.dict(os.environ, {}, clear=True)
    @patch("peagen._api_key.load_dotenv")
    def test_missing_environment_variable(self, mock_load_dotenv):
        """Test that function raises error when environment variable is not found"""
        mock_load_dotenv.return_value = False

        with pytest.raises(typer.Exit) as excinfo:
            _resolve_api_key("openai")
        assert excinfo.value.exit_code == 1

    @patch("peagen._api_key.load_dotenv")
    def test_custom_env_file(self, mock_load_dotenv):
        """Test that function loads custom .env file when provided"""
        with patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": "env-file-key-789"}, clear=True
        ):
            result = _resolve_api_key("anthropic", env_file=".env.test")
            assert result == "env-file-key-789"
            mock_load_dotenv.assert_called_once_with(".env.test")

    @patch("peagen._api_key.load_dotenv")
    def test_default_env_file(self, mock_load_dotenv):
        """Test that function loads default .env file when no file specified"""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "default-env-key"}, clear=True):
            result = _resolve_api_key("mistral")
            assert result == "default-env-key"
            mock_load_dotenv.assert_called_once_with()
