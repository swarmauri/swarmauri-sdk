import os
import tempfile
from unittest.mock import ANY, MagicMock, mock_open, patch

from swarmauri_prompt_j2prompttemplate import J2PromptTemplate
from peagen._utils._processing import (
    _create_context,
    _process_file,
    _process_project_files,
    _save_file,
)


class TestSaveFile:
    def test_save_file_creates_directory(self):
        """Test that _save_file creates the target directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            target_file = os.path.join(temp_dir, "new_dir", "test.txt")
            logger = MagicMock()

            with patch("builtins.open", mock_open()) as mock_file:
                _save_file("test content", target_file, logger)

                # Check that the directory was created
                assert os.path.exists(os.path.dirname(target_file))
                mock_file.assert_called_once_with(target_file, "w", encoding="utf-8")
                mock_file().write.assert_called_once_with("test content")
                logger.info.assert_called_once()

    def test_save_file_handles_exception(self):
        """Test that _save_file properly handles exceptions when saving fails."""
        logger = MagicMock()

        with patch("os.makedirs", side_effect=OSError("Permission denied")):
            _save_file("content", "/invalid/path/file.txt", logger)

            # Verify error was logged
            logger.error.assert_called_once()
            assert "Failed to save file" in logger.error.call_args[0][0]


class TestCreateContext:
    def test_create_context_with_project_only(self):
        """Test context creation with only project info."""
        file_record = {"PROJECT_NAME": "test_project"}
        project_global_attrs = {
            "NAME": "test_project",
            "DESCRIPTION": "Test description",
        }

        context = _create_context(file_record, project_global_attrs)

        assert "PROJ" in context
        assert context["PROJ"] == project_global_attrs
        assert "EXTRAS" in context["PROJ"]
        assert context["FILE"] == file_record

    def test_create_context_with_package(self):
        """Test context creation with project and package info."""
        file_record = {"PROJECT_NAME": "test_project", "PACKAGE_NAME": "test_package"}
        project_global_attrs = {
            "NAME": "test_project",
            "PACKAGES": [{"NAME": "test_package", "DESCRIPTION": "Test package"}],
        }

        context = _create_context(file_record, project_global_attrs)

        assert "PROJ" in context
        assert "PKG" in context
        assert context["PKG"]["NAME"] == "test_package"
        assert "EXTRAS" in context["PKG"]
        assert context["FILE"] == file_record

    def test_create_context_with_module(self):
        """Test context creation with project, package, and module info."""
        file_record = {
            "PROJECT_NAME": "test_project",
            "PACKAGE_NAME": "test_package",
            "MODULE_NAME": "test_module",
        }
        project_global_attrs = {
            "NAME": "test_project",
            "PACKAGES": [
                {
                    "NAME": "test_package",
                    "MODULES": [{"NAME": "test_module", "DESCRIPTION": "Test module"}],
                }
            ],
        }

        context = _create_context(file_record, project_global_attrs)

        assert "PROJ" in context
        assert "PKG" in context
        assert "MOD" in context
        assert context["MOD"]["NAME"] == "test_module"
        assert "EXTRAS" in context["MOD"]

    def test_create_context_with_logger(self):
        """Test context creation with logger."""
        file_record = {"PROJECT_NAME": "test_project"}
        project_global_attrs = {"NAME": "test_project"}
        logger = MagicMock()

        _create_context(file_record, project_global_attrs, logger)

        # Verify debug was called at least once
        assert logger.debug.call_count >= 1


class TestProcessFile:
    @patch("peagen._utils._processing._create_context")
    @patch("peagen._utils._processing._render_copy_template")
    @patch("peagen._utils._processing._save_file")
    def test_process_copy_file(self, mock_save, mock_render, mock_create_context):
        """Test processing a file with PROCESS_TYPE 'COPY'."""
        file_record = {"PROCESS_TYPE": "COPY", "RENDERED_FILE_NAME": "output.txt"}
        global_attrs = {}
        mock_create_context.return_value = {"test": "context"}
        mock_render.return_value = "Rendered content"

        _process_file(
            file_record=file_record,
            global_attrs=global_attrs,
            template_dir="templates",
            agent_env={},
            logger=MagicMock(),
        )

        mock_create_context.assert_called_once()
        mock_render.assert_called_once_with(
            file_record,
            {"test": "context"},
            ANY,
            ANY,
        )
        mock_save.assert_called_once_with(
            "Rendered content",
            "output.txt",
            ANY,
            0,
            1,
        )

    @patch("peagen._utils._processing._create_context")
    @patch("peagen._utils._processing._render_generate_template")
    @patch("peagen._utils._processing._save_file")
    def test_process_generate_file(self, mock_save, mock_render, mock_create_context):
        """Test processing a file with PROCESS_TYPE 'GENERATE'."""
        file_record = {
            "PROCESS_TYPE": "GENERATE",
            "RENDERED_FILE_NAME": "generated.py",
            "AGENT_PROMPT_TEMPLATE": "custom_template.j2",
        }
        global_attrs = {}
        mock_create_context.return_value = {"test": "context"}
        mock_render.return_value = "Generated content"

        _process_file(
            file_record=file_record,
            global_attrs=global_attrs,
            template_dir="templates",
            agent_env={},
            logger=MagicMock(),
        )

        mock_create_context.assert_called_once()
        mock_render.assert_called_once()
        mock_save.assert_called_once_with(
            "Generated content",
            "generated.py",
            ANY,
            0,
            1,
        )

    @patch("peagen._utils._processing._create_context")
    def test_process_unknown_type(self, mock_create_context):
        """Test processing a file with unknown PROCESS_TYPE."""
        file_record = {"PROCESS_TYPE": "UNKNOWN", "RENDERED_FILE_NAME": "file.txt"}
        mock_logger = MagicMock()

        result = _process_file(
            file_record=file_record,
            global_attrs={},
            template_dir="templates",
            agent_env={},
            logger=mock_logger,
        )

        assert result is False
        mock_logger.warning.assert_called_once()
        assert "Unknown PROCESS_TYPE" in mock_logger.warning.call_args[0][0]


class TestProcessProjectFiles:
    @patch("peagen._utils._processing._process_file")
    def test_process_project_files(self, mock_process_file):
        """Test processing multiple file records."""
        j2 = J2PromptTemplate()
        j2.templates_dir = ["default_templates"]

        global_attrs = {"TEMPLATE_SET": "default_templates"}
        file_records = [
            {"RENDERED_FILE_NAME": "file1.txt"},
            {"RENDERED_FILE_NAME": "file2.txt", "TEMPLATE_SET": "custom_templates"},
        ]
        mock_process_file.return_value = True

        _process_project_files(
            global_attrs=global_attrs,
            file_records=file_records,
            template_dir="templates",
            agent_env={},
            template_obj=j2,
            logger=MagicMock(),
        )

        # Check that _process_file was called twice
        assert mock_process_file.call_count == 2

    @patch("peagen._utils._processing._process_file")
    def test_process_project_files_with_template_set_change(self, mock_process_file):
        """Test template directory updates when TEMPLATE_SET changes."""
        global_attrs = {"TEMPLATE_SET": "default_templates"}
        file_records = [
            {"RENDERED_FILE_NAME": "file1.txt", "TEMPLATE_SET": "custom_templates"},
        ]
        mock_logger = MagicMock()
        mock_process_file.return_value = True

        # Set initial templates_dir
        j2 = J2PromptTemplate()
        j2.templates_dir = ["original_templates"]

        _process_project_files(
            global_attrs=global_attrs,
            file_records=file_records,
            template_dir="templates",
            agent_env={},
            template_obj=j2,
            logger=mock_logger,
        )

        # Check that template_obj.templates_dir was updated
        assert j2.templates_dir[0] == "custom_templates"
        assert mock_logger.debug.call_count >= 1

    @patch("peagen._utils._processing._process_file")
    def test_process_project_files_stops_on_false(self, mock_process_file):
        """Test that processing stops if _process_file returns False."""
        global_attrs = {}
        j2 = J2PromptTemplate()
        file_records = [
            {"RENDERED_FILE_NAME": "file1.txt"},
            {"RENDERED_FILE_NAME": "file2.txt"},
            {"RENDERED_FILE_NAME": "file3.txt"},
        ]
        # Make the second file processing fail
        mock_process_file.side_effect = [True, False, True]

        _process_project_files(
            global_attrs=global_attrs,
            file_records=file_records,
            template_dir="templates",
            agent_env={},
            template_obj=j2,
            logger=MagicMock(),
        )

        # Check that _process_file was called only twice (stopped after the False return)
        assert mock_process_file.call_count == 2
