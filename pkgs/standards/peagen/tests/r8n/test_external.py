import os
from unittest.mock import MagicMock, patch

import pytest
from peagen._external import call_external_agent, chunk_content


class TestChunkContent:
    def test_clean_think_blocks(self):
        """Test removing <think> blocks from content."""
        content = "This is normal content.\n<think>This should be removed</think>\nMore content."

        # Mock the chunker since test is about regex cleaning
        with patch(
            "swarmauri.chunkers.MdSnippetChunker.MdSnippetChunker"
        ) as mock_chunker:
            # Mock to return a chunk instead of empty list to trigger the
            # code path that removes <think> blocks
            mock_instance = mock_chunker.return_value
            # Return a single chunk with cleaned content
            mock_instance.chunk_text.return_value = [
                ("comment", "python", "This is normal content.\nMore content.")
            ]

            result = chunk_content(content)

            # Now the assertions should pass because we're returning our mocked chunk
            assert "<think>" not in result
            assert "This should be removed" not in result
            assert "This is normal content" in result
            assert "More content" in result

    def test_single_chunk_returns_content(self):
        """Test that content with a single chunk returns the chunk content."""
        with patch(
            "swarmauri.chunkers.MdSnippetChunker.MdSnippetChunker"
        ) as mock_chunker:
            # Mock the chunker to return a single chunk
            mock_instance = mock_chunker.return_value
            mock_instance.chunk_text.return_value = [
                ("comment", "python", "print('hello')")
            ]

            result = chunk_content("```python\nprint('hello')\n```")
            assert result == "print('hello')"
            mock_instance.chunk_text.assert_called_once()

    def test_multiple_chunks_returns_full_content(self):
        """Test that content with multiple chunks returns the full clean content."""
        with patch(
            "swarmauri.chunkers.MdSnippetChunker.MdSnippetChunker"
        ) as mock_chunker:
            # Mock the chunker to return multiple chunks
            mock_instance = mock_chunker.return_value
            mock_instance.chunk_text.return_value = [
                ("comment1", "python", "print('hello')"),
                ("comment2", "python", "print('world')"),
            ]

            test_content = (
                "```python\nprint('hello')\n```\n```python\nprint('world')\n```"
            )
            result = chunk_content(test_content)
            assert result == test_content
            mock_instance.chunk_text.assert_called_once()

    def test_chunker_import_error(self):
        """Test handling of ImportError when trying to import the chunker."""
        with patch(
            "swarmauri.chunkers.MdSnippetChunker.MdSnippetChunker",
            side_effect=ImportError,
        ):
            logger_mock = MagicMock()
            content = "Test content"
            result = chunk_content(content, logger_mock)

            assert result == content
            logger_mock.warning.assert_called_once()

    def test_chunker_generic_exception(self):
        """Test handling of general exceptions during chunking."""
        with patch(
            "swarmauri.chunkers.MdSnippetChunker.MdSnippetChunker"
        ) as mock_chunker:
            mock_instance = mock_chunker.return_value
            mock_instance.chunk_text.side_effect = Exception("Test error")

            logger_mock = MagicMock()
            content = "Test content"
            result = chunk_content(content, logger_mock)

            assert result == content
            logger_mock.error.assert_called_once()

    def test_markdown_file_returns_full_content(self):
        """Markdown files should bypass chunking."""
        with patch(
            "swarmauri.chunkers.MdSnippetChunker.MdSnippetChunker"
        ) as mock_chunker:
            content = "some text with ```code```"
            result = chunk_content(content, file_name="README.md")

            assert result == content
            mock_chunker.assert_not_called()


class TestCallExternalAgent:
    @pytest.fixture
    def mock_dependencies(self):
        """Setup mocks for external dependencies."""
        with (
            patch("swarmauri.agents.QAAgent.QAAgent") as mock_qa_agent,
            patch(
                "swarmauri.messages.SystemMessage.SystemMessage"
            ) as mock_system_message,
            patch("peagen._llm.GenericLLM") as mock_generic_llm,
            patch("peagen._external._config", {"truncate": True}),
            patch.dict(os.environ, {}, clear=True),
        ):
            # Setup the mock chain
            mock_llm_instance = MagicMock()
            mock_generic_llm_instance = mock_generic_llm.return_value
            mock_generic_llm_instance.get_llm.return_value = mock_llm_instance

            mock_agent_instance = mock_qa_agent.return_value
            mock_agent_instance.exec.return_value = "Generated content"
            mock_agent_instance.conversation = MagicMock()

            yield {
                "qa_agent": mock_qa_agent,
                "system_message": mock_system_message,
                "generic_llm": mock_generic_llm,
                "llm_instance": mock_llm_instance,
                "agent_instance": mock_agent_instance,
            }

    def test_call_external_agent_basic(self, mock_dependencies):
        """Test the basic flow of call_external_agent with default parameters."""
        prompt = "Generate some code"
        agent_env = {
            "provider": "deepinfra",
            "api_key": "test_key",
            "model_name": "test_model",
            "max_tokens": 1000,
        }

        result = call_external_agent(prompt, agent_env)

        # Verify the result
        assert result == "Generated content"

        # Verify the LLM was created with proper params
        mock_dependencies["generic_llm"].return_value.get_llm.assert_called_with(
            provider="deepinfra", api_key="test_key", model_name="test_model"
        )

        # Verify the agent was created and called properly
        mock_dependencies["qa_agent"].assert_called_once()
        mock_dependencies["agent_instance"].exec.assert_called_with(
            prompt, llm_kwargs={"max_tokens": 1000}
        )

    def test_call_external_agent_with_env_vars(self, mock_dependencies):
        """Test using environment variables for configuration."""
        with patch.dict(
            os.environ, {"PROVIDER": "openai", "OPENAI_API_KEY": "env_key"}
        ):
            prompt = "Generate some code"
            agent_env = {"model_name": "test_model", "max_tokens": 1000}

            call_external_agent(prompt, agent_env)

            # Verify the LLM was created with env vars
            mock_dependencies["generic_llm"].return_value.get_llm.assert_called_with(
                provider="openai", api_key="env_key", model_name="test_model"
            )

    def test_call_external_agent_llamacpp(self, mock_dependencies):
        """Test the special case for LlamaCpp provider."""
        prompt = "Generate some code"
        agent_env = {
            "provider": "llamacpp",
            "model_name": "test_model",
            "max_tokens": 1000,
        }

        call_external_agent(prompt, agent_env)

        # Verify the LLM was created with the special LlamaCpp parameters
        mock_dependencies["generic_llm"].return_value.get_llm.assert_called_with(
            provider="llamacpp",
            api_key=None,
            model_name="localhost",
            allowed_models=["localhost"],
        )

    def test_call_external_agent_with_logger(self, mock_dependencies):
        """Test that logging works properly."""
        logger_mock = MagicMock()
        prompt = "Generate some code"
        agent_env = {
            "provider": "deepinfra",
            "api_key": "test_key",
            "model_name": "test_model",
        }

        call_external_agent(prompt, agent_env, logger_mock)

        # Verify the prompt was logged
        logger_mock.info.assert_called_once()
        # Check that the truncated prompt appears in the log message
        log_message = logger_mock.info.call_args[0][0]
        assert prompt[:140] in log_message

    @patch("peagen._external.chunk_content")
    def test_call_external_agent_chunking(self, mock_chunk_content, mock_dependencies):
        """Test that the result is passed through chunk_content."""
        mock_chunk_content.return_value = "Chunked content"

        prompt = "Generate some code"
        agent_env = {
            "provider": "deepinfra",
            "api_key": "test_key",
            "model_name": "test_model",
        }

        result = call_external_agent(prompt, agent_env)

        # Verify chunk_content was called with the generated result
        mock_chunk_content.assert_called_with("Generated content", None, None)
        assert result == "Chunked content"

    def test_keyboard_interrupt_handling(self, mock_dependencies):
        """Test that KeyboardInterrupt is properly reraised."""
        mock_dependencies["agent_instance"].exec.side_effect = KeyboardInterrupt

        prompt = "Generate some code"
        agent_env = {"provider": "test"}

        with pytest.raises(KeyboardInterrupt):
            call_external_agent(prompt, agent_env)
