import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest
from peagen._rendering import _render_copy_template, _render_generate_template


@pytest.mark.unit
class TestRendering:
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing"""
        return MagicMock()

    @pytest.fixture
    def temp_template_file(self):
        """Create a temporary template file for testing"""
        with tempfile.NamedTemporaryFile(suffix=".j2", delete=False, mode="w") as f:
            f.write("Hello, {{ name }}!")
        try:
            yield f.name
        finally:
            os.unlink(f.name)

    @pytest.fixture
    def mock_template_file(self):
        """Create a mock template file path for testing"""
        return "path/to/template.j2"

    @pytest.fixture
    def file_record(self):
        """Create a basic file record for testing"""
        return {
            "FILE_NAME": "path/to/template.j2",
            "RENDERED_FILE_NAME": "output.txt",
            "EXTRAS": {"PURPOSE": "Test purpose", "DESCRIPTION": "Test description"},
        }

    @pytest.fixture
    def context(self):
        """Create a context dictionary for testing"""
        return {
            "name": "World",
            "PROJECT_NAME": "TestProject",
            "PACKAGE_NAME": "TestPackage",
        }

    @patch("peagen._rendering.j2pt")
    def test_render_copy_template_success(
        self, mock_j2pt, file_record, context, mock_logger
    ):
        """Test successful rendering of a copy template"""
        mock_j2pt.fill.return_value = "Hello, World!"

        result = _render_copy_template(file_record, context, mock_logger)

        assert result == "Hello, World!"
        mock_j2pt.set_template.assert_called_once()
        mock_j2pt.fill.assert_called_once_with(context)
        mock_logger.error.assert_not_called()

    @patch("peagen._rendering.j2pt")
    def test_render_copy_template_exception(
        self, mock_j2pt, file_record, context, mock_logger
    ):
        """Test handling of exceptions during copy template rendering"""
        mock_j2pt.set_template.side_effect = Exception("Template error")

        result = _render_copy_template(file_record, context, mock_logger)

        assert result == ""
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Failed" in error_msg and "render copy template" in error_msg

    @patch("peagen._rendering.j2pt")
    def test_render_copy_template_no_logger(self, mock_j2pt, file_record, context):
        """Test rendering with no logger provided"""
        mock_j2pt.set_template.side_effect = Exception("Template error")

        result = _render_copy_template(file_record, context)

        assert result == ""

    @patch("peagen._external.call_external_agent")  # Fixed patch target
    @patch("peagen._rendering.j2pt")
    def test_render_generate_template_success(
        self, mock_j2pt, mock_call_agent, file_record, context, mock_logger
    ):
        """Test successful rendering of a generate template"""
        # Set up the mocks
        mock_j2pt.fill.return_value = "Rendered prompt"
        mock_call_agent.return_value = "Generated content"

        # Call the function
        result = _render_generate_template(
            file_record, context, "agent_prompt.j2", {}, mock_logger
        )

        # Verify the result and interactions
        assert result == "Generated content"
        mock_j2pt.set_template.assert_called_once()
        mock_j2pt.fill.assert_called_once_with(context)
        mock_call_agent.assert_called_once_with("Rendered prompt", {}, mock_logger)
        mock_logger.error.assert_not_called()

    @patch("peagen._external.call_external_agent")
    @patch("peagen._rendering.j2pt")
    def test_render_generate_template_exception(
        self, mock_j2pt, mock_call_agent, file_record, context, mock_logger
    ):
        """Test handling of exceptions during generate template rendering"""
        mock_j2pt.set_template.side_effect = Exception("Template error")

        result = _render_generate_template(
            file_record, context, "agent_prompt.j2", {}, mock_logger
        )

        assert result == ""
        mock_logger.error.assert_called_once()
        assert (
            "Failed" in mock_logger.error.call_args[0][0]
            and "render generate template" in mock_logger.error.call_args[0][0]
        )
        mock_call_agent.assert_not_called()

    @patch("peagen._external.call_external_agent")
    @patch("peagen._rendering.j2pt")
    def test_render_generate_template_with_agent_env(
        self, mock_j2pt, mock_call_agent, file_record, context, mock_logger
    ):
        """Test generate template rendering with custom agent environment"""
        # Set up the mocks
        mock_j2pt.fill.return_value = "Rendered prompt"
        mock_call_agent.return_value = "Generated content"

        agent_env = {
            "provider": "test-provider",
            "api_key": "test-key",
            "model_name": "test-model",
        }

        # Call the function
        result = _render_generate_template(
            file_record, context, "agent_prompt.j2", agent_env, mock_logger
        )

        # Verify the result and interactions
        assert result == "Generated content"
        mock_call_agent.assert_called_once_with(
            "Rendered prompt", agent_env, mock_logger
        )

    @patch("peagen._external.call_external_agent")
    @patch("peagen._rendering.j2pt")
    def test_render_generate_template_no_logger(
        self, mock_j2pt, mock_call_agent, file_record, context
    ):
        """Test generate template rendering with no logger provided"""
        mock_j2pt.set_template.side_effect = Exception("Template error")

        # This should not raise an exception even without a logger
        result = _render_generate_template(file_record, context, "agent_prompt.j2", {})

        assert result == ""
