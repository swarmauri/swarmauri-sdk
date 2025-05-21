import os
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest
from peagen.core import Peagen


class TestPeagen:
    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger for testing."""
        logger = MagicMock()
        return logger

    @pytest.fixture
    def basic_peagen(self, mock_logger):
        """Create a basic Peagen instance for testing."""
        instance = Peagen(
            projects_payload_path="test_payload.yaml",
            template_base_dir="/test/templates",
        )
        instance.logger = mock_logger
        return instance

    def test_initialization(self):
        """Test basic initialization of Peagen."""
        peagen = Peagen(projects_payload_path="test_payload.yaml")
        assert peagen.projects_payload_path == "test_payload.yaml"
        assert peagen.template_base_dir is None
        assert isinstance(peagen.agent_env, dict)
        assert peagen.j2pt is not None
        assert peagen.base_dir == os.getcwd()
        assert peagen.projects_list == []

    def test_setup_env(self):
        """Test that setup_env properly configures paths."""
        with patch("peagen.templates.__path__", ["/installed/templates"]):
            peagen = Peagen(
                projects_payload_path="test_payload.yaml",
                template_base_dir="/custom/templates",
                additional_package_dirs=[Path("/additional/templates")],
            )

            # Check namespace_dirs
            assert "/installed/templates" in peagen.namespace_dirs
            assert peagen.base_dir in peagen.namespace_dirs
            assert "/custom/templates" in peagen.namespace_dirs

            # Check j2pt templates_dir
            assert Path("/additional/templates") in peagen.j2pt.templates_dir
            assert peagen.base_dir in peagen.j2pt.templates_dir
            assert "/custom/templates" in peagen.j2pt.templates_dir

    def test_update_templates_dir(self, basic_peagen):
        """Test update_templates_dir method."""
        # Setup
        basic_peagen.additional_package_dirs = [Path("/add1"), Path("/add2")]

        # Call method
        basic_peagen.update_templates_dir("/package/templates")

        # Check updated templates_dir
        assert basic_peagen.j2pt.templates_dir[0] == os.path.normpath(
            "/package/templates"
        )
        assert basic_peagen.j2pt.templates_dir[1] == os.path.normpath(
            basic_peagen.base_dir
        )
        assert os.path.normpath("/add1") in basic_peagen.j2pt.templates_dir
        assert os.path.normpath("/add2") in basic_peagen.j2pt.templates_dir

    def test_get_template_dir_any_found(self, basic_peagen):
        """Test get_template_dir_any when template set exists."""
        # Setup
        basic_peagen.namespace_dirs = ["/dir1", "/dir2", "/dir3"]

        with patch("pathlib.Path.is_dir", return_value=True):
            result = basic_peagen.get_template_dir_any("test_templates")

            # Should return the first matching directory
            assert result == Path("/dir1/test_templates").resolve()

    def test_get_template_dir_any_not_found(self, basic_peagen):
        """Test get_template_dir_any when template set doesn't exist."""
        # Setup
        basic_peagen.namespace_dirs = ["/dir1", "/dir2", "/dir3"]

        with patch("pathlib.Path.is_dir", return_value=False):
            with pytest.raises(ValueError) as excinfo:
                basic_peagen.get_template_dir_any("nonexistent_templates")

            assert "not found in any of" in str(excinfo.value)

    def test_load_projects_dict(self, basic_peagen):
        """Test load_projects when YAML contains a dict with PROJECTS key."""
        yaml_content = """
        PROJECTS:
          - NAME: project1
            VERSION: 1.0.0
          - NAME: project2
            VERSION: 2.0.0
        """

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            result = basic_peagen.load_projects()

            assert len(result) == 2
            assert result[0]["NAME"] == "project1"
            assert result[1]["NAME"] == "project2"
            assert basic_peagen.projects_list == result

    def test_load_projects_list(self, basic_peagen):
        """Test load_projects when YAML contains a list directly."""
        yaml_content = """
        - NAME: project1
          VERSION: 1.0.0
        - NAME: project2
          VERSION: 2.0.0
        """

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            result = basic_peagen.load_projects()

            assert len(result) == 2
            assert result[0]["NAME"] == "project1"
            assert result[1]["NAME"] == "project2"
            assert basic_peagen.projects_list == result

    def test_load_projects_error(self, basic_peagen):
        """Test load_projects with file error."""
        with patch("builtins.open", side_effect=Exception("File not found")):
            result = basic_peagen.load_projects()

            assert result == []
            assert basic_peagen.projects_list == []
            basic_peagen.logger.error.assert_called_once()

    def test_process_all_projects_empty(self, basic_peagen):
        """Test process_all_projects with no projects."""
        # Instead of patching the instance method, use monkeypatch to replace it temporarily
        with patch("peagen.core.Peagen.load_projects", return_value=[]):
            result = basic_peagen.process_all_projects()

            assert result == []

    def test_process_all_projects(self, basic_peagen):
        """Test process_all_projects with multiple projects."""
        project1 = {"NAME": "project1"}
        project2 = {"NAME": "project2"}
        basic_peagen.projects_list = [project1, project2]

        # Use module-level patching instead of object patching
        with patch(
            "peagen.core.Peagen.process_single_project",
            side_effect=[(["file1", "file2"], 0), (["file3", "file4"], 0)],
        ):
            result = basic_peagen.process_all_projects()

            assert result == [["file1", "file2"], ["file3", "file4"]]

    @patch("os.path.isfile", return_value=True)
    def test_process_single_project_no_packages(self, mock_isfile, basic_peagen):
        """Test process_single_project with a project that has no packages."""
        project = {"NAME": "test_project", "PACKAGES": []}

        result, start_idx = basic_peagen.process_single_project(project)

        assert result == []
        assert start_idx == 0
        basic_peagen.logger.warning.assert_called_with(
            "[test_project] No file records found at all."
        )

    @patch("os.path.isfile", return_value=True)
    @patch("yaml.safe_load")
    def test_process_single_project_with_files(
        self, mock_yaml_load, mock_isfile, basic_peagen
    ):
        """Test process_single_project with a normal project."""
        # Setup project with packages
        project = {
            "NAME": "test_project",
            "TEMPLATE_SET": "default",
            "PACKAGES": [{"NAME": "package1"}],
        }

        # Mock template rendering and processing
        rendered_yaml = "mock rendered yaml"
        file_records = [
            {
                "RENDERED_FILE_NAME": "file1.py",
                "TEMPLATE_SET": "/test/templates/default",
            },
            {
                "RENDERED_FILE_NAME": "file2.py",
                "TEMPLATE_SET": "/test/templates/default",
            },
        ]

        # Use patch instead of patch.object
        with patch(
            "peagen.core.Peagen.get_template_dir_any",
            return_value=Path("/test/templates/default"),
        ):
            with patch("swarmauri_prompt_j2prompttemplate.j2pt.set_template"):
                with patch(
                    "swarmauri_prompt_j2prompttemplate.j2pt.fill",
                    return_value=rendered_yaml,
                ):
                    # Mock YAML parsing of rendered template
                    mock_yaml_load.return_value = {"FILES": file_records}

                    # Mock topological sorting
                    with patch(
                        "peagen.core._topological_sort", return_value=file_records
                    ):
                        # Mock file processing
                        with patch("peagen.core._process_project_files"):
                            result, idx = basic_peagen.process_single_project(project)

                            # Check results
                            assert result == file_records
                            assert idx == 0
                            # Check logger calls
                            basic_peagen.logger.info.assert_called()

    @patch("os.path.isfile", return_value=True)
    def test_process_single_project_with_start_file(self, mock_isfile, basic_peagen):
        """Test process_single_project with start_file parameter."""
        # Setup project
        project = {
            "NAME": "test_project",
            "TEMPLATE_SET": "default",
            "PACKAGES": [{"NAME": "package1"}],
        }

        # Mock file records and template rendering
        file_records = [
            {"RENDERED_FILE_NAME": "file1.py"},
            {"RENDERED_FILE_NAME": "file2.py"},
            {"RENDERED_FILE_NAME": "file3.py"},
        ]

        # Correct patching order matching the working test
        with patch(
            "peagen.core.Peagen.get_template_dir_any",
            return_value=Path("/test/templates/default"),
        ):
            with patch("swarmauri_prompt_j2prompttemplate.j2pt.set_template"):
                with patch(
                    "swarmauri_prompt_j2prompttemplate.j2pt.fill",
                    return_value="rendered content",
                ):
                    with patch("yaml.safe_load", return_value={"FILES": file_records}):
                        # Use non-transitive sort but with start_file
                        with patch("peagen.core._config", {"transitive": False}):
                            with patch(
                                "peagen.core._topological_sort",
                                return_value=file_records,
                            ):
                                with patch("peagen.core._process_project_files"):
                                    # Test with start_file="file2.py"
                                    result, idx = basic_peagen.process_single_project(
                                        project, start_file="file2.py"
                                    )

                                    # Should return only file2 and file3
                                    assert len(result) == 2
                                    assert result[0]["RENDERED_FILE_NAME"] == "file2.py"
                                    assert result[1]["RENDERED_FILE_NAME"] == "file3.py"

    @patch("os.path.isfile", return_value=True)
    def test_process_single_project_with_start_idx(self, mock_isfile, basic_peagen):
        """Test process_single_project with start_idx parameter."""
        # Setup project
        project = {
            "NAME": "test_project",
            "TEMPLATE_SET": "default",
            "PACKAGES": [{"NAME": "package1"}],
        }

        # Mock file records and template rendering
        file_records = [
            {"RENDERED_FILE_NAME": "file1.py"},
            {"RENDERED_FILE_NAME": "file2.py"},
            {"RENDERED_FILE_NAME": "file3.py"},
        ]

        with patch(
            "peagen.core.Peagen.get_template_dir_any",
            return_value=Path("/test/templates/default"),
        ):
            with patch("swarmauri_prompt_j2prompttemplate.j2pt.set_template"):
                with patch(
                    "swarmauri_prompt_j2prompttemplate.j2pt.fill",
                    return_value="rendered content",
                ):
                    with patch("yaml.safe_load", return_value={"FILES": file_records}):
                        with patch(
                            "peagen.core._topological_sort", return_value=file_records
                        ):
                            with patch("peagen.core._process_project_files"):
                                # Test with start_idx=1
                                result, idx = basic_peagen.process_single_project(
                                    project, start_idx=1
                                )

                                # Should return only file2 and file3
                                assert len(result) == 2
                                assert result[0]["RENDERED_FILE_NAME"] == "file2.py"
                                assert idx == 1

    @patch("os.path.isfile", return_value=True)
    def test_process_single_project_with_transitive_sorting(
        self, mock_isfile, basic_peagen
    ):
        """Test process_single_project with transitive sorting."""
        # Setup project
        project = {
            "NAME": "test_project",
            "TEMPLATE_SET": "default",
            "PACKAGES": [{"NAME": "package1"}],
        }

        # Mock file records and template rendering
        file_records = [
            {"RENDERED_FILE_NAME": "file1.py"},
            {"RENDERED_FILE_NAME": "file2.py", "DEPENDS": ["file1.py"]},
            {"RENDERED_FILE_NAME": "file3.py", "DEPENDS": ["file2.py"]},
        ]

        transitive_records = [
            {"RENDERED_FILE_NAME": "file2.py", "DEPENDS": ["file1.py"]},
            {"RENDERED_FILE_NAME": "file3.py", "DEPENDS": ["file2.py"]},
        ]

        with patch(
            "peagen.core.Peagen.get_template_dir_any",
            return_value=Path("/test/templates/default"),
        ):
            with patch("swarmauri_prompt_j2prompttemplate.j2pt.set_template"):
                with patch(
                    "swarmauri_prompt_j2prompttemplate.j2pt.fill",
                    return_value="rendered content",
                ):
                    with patch("yaml.safe_load", return_value={"FILES": file_records}):
                        # Use transitive sort with start_file
                        with patch("peagen.core._config", {"transitive": True}):
                            with patch(
                                "peagen.core._transitive_dependency_sort",
                                return_value=transitive_records,
                            ):
                                with patch("peagen.core._process_project_files"):
                                    # Test with start_file="file2.py"
                                    result, idx = basic_peagen.process_single_project(
                                        project, start_file="file2.py"
                                    )

                                    # Should return the transitive closure
                                    assert result == transitive_records

    def test_analyze_all_projects_no_conflicts(self, basic_peagen):
        """Validate analyze_all_projects when no conflicts exist."""
        slug_map = {
            "proj1": {
                "files": ["a.py", "b.py"],
                "packages": [{"NAME": "pkgA", "VERSION": "1.0"}],
            },
            "proj2": {
                "files": ["c.py"],
                "packages": [{"NAME": "pkgA", "VERSION": "1.0"}],
            },
        }

        # Should not raise any errors
        basic_peagen.analyze_all_projects(slug_map)

    def test_analyze_all_projects_file_conflict(self, basic_peagen):
        """File name collision across projects should raise ValueError."""
        slug_map = {
            "proj1": {"files": ["shared.py"], "packages": []},
            "proj2": {"files": ["shared.py"], "packages": []},
        }

        with pytest.raises(ValueError):
            basic_peagen.analyze_all_projects(slug_map)

    def test_analyze_all_projects_version_conflict(self, basic_peagen):
        """Package version mismatch should raise ValueError."""
        slug_map = {
            "proj1": {
                "files": ["a.py"],
                "packages": [{"NAME": "pkgA", "VERSION": "1.0"}],
            },
            "proj2": {
                "files": ["b.py"],
                "packages": [{"NAME": "pkgA", "VERSION": "2.0"}],
            },
        }

        with pytest.raises(ValueError):
            basic_peagen.analyze_all_projects(slug_map)
