from unittest.mock import mock_open, patch

import pytest

# Import the functions to test
from peagen._updates import (
    GLOBAL_PROJECTS_DATA,
    TEMPLATE_DATA,
    save_global_projects,
    save_template,
    update_global_value,
    update_module_value,
    update_package_value,
    update_template,
)


class TestGlobalProjectsOperations:
    @pytest.fixture(autouse=True)
    def reset_global_data(self):
        """Reset global data before and after each test."""
        # Store original data
        original_global_data = GLOBAL_PROJECTS_DATA.copy()
        # Clear for test
        GLOBAL_PROJECTS_DATA.clear()

        yield

        # Restore original data after test
        GLOBAL_PROJECTS_DATA.clear()
        GLOBAL_PROJECTS_DATA.update(original_global_data)

    def test_update_global_value(self):
        """Test updating a global value."""
        # Test updating a simple value
        update_global_value("VERSION", "1.0.0")
        assert GLOBAL_PROJECTS_DATA["VERSION"] == "1.0.0"

        # Test updating a complex value
        complex_value = {"name": "test", "value": 42}
        update_global_value("CONFIG", complex_value)
        assert GLOBAL_PROJECTS_DATA["CONFIG"] == complex_value

    def test_update_package_value_replace(self):
        """Test updating a package value with replace mode."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [{"NAME": "test_package", "VERSION": "0.1.0"}],
            }
        ]

        # Test update
        result = update_package_value(
            "test_project", "test_package", "VERSION", "1.0.0"
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["VERSION"] == "1.0.0"

    def test_update_package_value_append(self):
        """Test updating a package value with append mode."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [{"NAME": "test_package", "DEPENDENCIES": ["dep1"]}],
            }
        ]

        # Test append with single item
        result = update_package_value(
            "test_project", "test_package", "DEPENDENCIES", "dep2", mode="append"
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["DEPENDENCIES"] == [
            "dep1",
            "dep2",
        ]

        # Test append with list
        result = update_package_value(
            "test_project",
            "test_package",
            "DEPENDENCIES",
            ["dep3", "dep4"],
            mode="append",
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["DEPENDENCIES"] == [
            "dep1",
            "dep2",
            "dep3",
            "dep4",
        ]

    def test_update_package_value_remove(self):
        """Test updating a package value with remove mode."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [
                    {"NAME": "test_package", "DEPENDENCIES": ["dep1", "dep2", "dep3"]}
                ],
            }
        ]

        # Test remove single item
        result = update_package_value(
            "test_project", "test_package", "DEPENDENCIES", "dep2", mode="remove"
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["DEPENDENCIES"] == [
            "dep1",
            "dep3",
        ]

        # Test remove list
        result = update_package_value(
            "test_project", "test_package", "DEPENDENCIES", ["dep1"], mode="remove"
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["DEPENDENCIES"] == [
            "dep3"
        ]

    def test_update_package_nonexistent_project(self):
        """Test updating a package in a non-existent project."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [{"NAME": "other_project"}]

        # Test update
        result = update_package_value("nonexistent", "test_package", "VERSION", "1.0.0")

        # Verify no change and return value is False
        assert result is False
        assert len(GLOBAL_PROJECTS_DATA["PROJECTS"]) == 1
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["NAME"] == "other_project"

    def test_update_package_nonexistent_package(self):
        """Test updating a non-existent package."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {"NAME": "test_project", "PACKAGES": [{"NAME": "other_package"}]}
        ]

        # Test update
        result = update_package_value("test_project", "nonexistent", "VERSION", "1.0.0")

        # Verify no change and return value is False
        assert result is False

    def test_update_module_value_replace(self):
        """Test updating a module value with replace mode."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [
                    {
                        "NAME": "test_package",
                        "MODULES": [{"NAME": "test_module", "VERSION": "0.1.0"}],
                    }
                ],
            }
        ]

        # Test update
        result = update_module_value(
            "test_project", "test_package", "test_module", "VERSION", "1.0.0"
        )

        # Verify result
        assert result is True
        assert (
            GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["MODULES"][0]["VERSION"]
            == "1.0.0"
        )

    def test_update_module_value_append(self):
        """Test updating a module value with append mode."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [
                    {
                        "NAME": "test_package",
                        "MODULES": [{"NAME": "test_module", "FUNCTIONS": ["func1"]}],
                    }
                ],
            }
        ]

        # Test append
        result = update_module_value(
            "test_project",
            "test_package",
            "test_module",
            "FUNCTIONS",
            ["func2", "func3"],
            mode="append",
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["MODULES"][0][
            "FUNCTIONS"
        ] == ["func1", "func2", "func3"]

    def test_update_module_value_remove(self):
        """Test updating a module value with remove mode."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [
                    {
                        "NAME": "test_package",
                        "MODULES": [
                            {
                                "NAME": "test_module",
                                "FUNCTIONS": ["func1", "func2", "func3"],
                            }
                        ],
                    }
                ],
            }
        ]

        # Test remove
        result = update_module_value(
            "test_project",
            "test_package",
            "test_module",
            "FUNCTIONS",
            ["func1", "func3"],
            mode="remove",
        )

        # Verify result
        assert result is True
        assert GLOBAL_PROJECTS_DATA["PROJECTS"][0]["PACKAGES"][0]["MODULES"][0][
            "FUNCTIONS"
        ] == ["func2"]

    def test_update_module_nonexistent(self):
        """Test updating a non-existent module."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["PROJECTS"] = [
            {
                "NAME": "test_project",
                "PACKAGES": [
                    {"NAME": "test_package", "MODULES": [{"NAME": "other_module"}]}
                ],
            }
        ]

        # Test update
        result = update_module_value(
            "test_project", "test_package", "nonexistent", "VERSION", "1.0.0"
        )

        # Verify no change and return value is False
        assert result is False

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_dump")
    def test_save_global_projects(self, mock_yaml_dump, mock_file):
        """Test saving global projects data to a file."""
        # Setup test data
        GLOBAL_PROJECTS_DATA["VERSION"] = "1.0.0"
        GLOBAL_PROJECTS_DATA["PROJECTS"] = []

        # Call function
        save_global_projects("/path/to/projects.yaml")

        # Verify file was opened for writing
        mock_file.assert_called_once_with(
            "/path/to/projects.yaml", "w", encoding="utf-8"
        )

        # Verify yaml.safe_dump was called with the global data
        mock_yaml_dump.assert_called_once()
        args, _ = mock_yaml_dump.call_args
        assert args[0] == GLOBAL_PROJECTS_DATA


class TestTemplateOperations:
    @pytest.fixture(autouse=True)
    def reset_template_data(self):
        """Reset template data before and after each test."""
        # Store original data
        original_template_data = TEMPLATE_DATA.copy()
        # Clear for test
        TEMPLATE_DATA.clear()

        yield

        # Restore original data after test
        TEMPLATE_DATA.clear()
        TEMPLATE_DATA.update(original_template_data)

    def test_update_template_add_file(self):
        """Test adding a file record to the template."""
        # Test data
        file_record = {
            "id": "file1",
            "path": "/path/to/file.py",
            "content": "print('Hello, world!')",
        }

        # Call function
        update_template("add", "file", file_record)

        # Verify file was added
        assert "FILES" in TEMPLATE_DATA
        assert len(TEMPLATE_DATA["FILES"]) == 1
        assert TEMPLATE_DATA["FILES"][0] == file_record

    def test_update_template_add_dependency(self):
        """Test adding a dependency to the template."""
        # Test data
        dependency = {"name": "requests", "version": ">=2.25.0"}

        # Call function
        update_template("add", "dependency", dependency)

        # Verify dependency was added
        assert "DEPENDENCIES" in TEMPLATE_DATA
        assert len(TEMPLATE_DATA["DEPENDENCIES"]) == 1
        assert TEMPLATE_DATA["DEPENDENCIES"][0] == dependency

    def test_update_template_update_file(self):
        """Test updating a file record in the template."""
        # Setup test data
        TEMPLATE_DATA["FILES"] = [
            {"id": "file1", "path": "/old/path.py", "content": "old content"},
            {"id": "file2", "path": "/other/path.py", "content": "other content"},
        ]

        # Test data for update
        updated_record = {
            "id": "file1",
            "path": "/new/path.py",
            "content": "new content",
        }

        # Call function
        update_template("update", "file", updated_record)

        # Verify file was updated
        assert len(TEMPLATE_DATA["FILES"]) == 2
        assert TEMPLATE_DATA["FILES"][0]["path"] == "/new/path.py"
        assert TEMPLATE_DATA["FILES"][0]["content"] == "new content"
        # Check that other files weren't affected
        assert TEMPLATE_DATA["FILES"][1]["id"] == "file2"

    def test_update_template_update_nonexistent(self):
        """Test updating a non-existent file record."""
        # Setup test data
        TEMPLATE_DATA["FILES"] = [{"id": "file1", "path": "/path.py"}]

        # Call function with non-existent id
        update_template("update", "file", {"id": "nonexistent", "path": "/new.py"})

        # Verify no changes
        assert len(TEMPLATE_DATA["FILES"]) == 1
        assert TEMPLATE_DATA["FILES"][0]["path"] == "/path.py"

    def test_update_template_remove_file(self):
        """Test removing a file record from the template."""
        # Setup test data
        TEMPLATE_DATA["FILES"] = [
            {"id": "file1", "path": "/path1.py"},
            {"id": "file2", "path": "/path2.py"},
        ]

        # Call function
        update_template("remove", "file", {"id": "file1"})

        # Verify file was removed
        assert len(TEMPLATE_DATA["FILES"]) == 1
        assert TEMPLATE_DATA["FILES"][0]["id"] == "file2"

    def test_update_template_remove_nonexistent(self):
        """Test removing a non-existent file record."""
        # Setup test data
        TEMPLATE_DATA["FILES"] = [{"id": "file1", "path": "/path.py"}]

        # Call function
        update_template("remove", "file", {"id": "nonexistent"})

        # Verify no changes
        assert len(TEMPLATE_DATA["FILES"]) == 1

    def test_update_template_unknown_operation(self):
        """Test handling unknown operations."""
        # Call with invalid operation
        update_template("invalid", "file", {"id": "file1"})

        # Verify no changes (should just print error)
        assert "FILES" not in TEMPLATE_DATA

    @patch("builtins.open", new_callable=mock_open)
    @patch("yaml.safe_dump")
    def test_save_template(self, mock_yaml_dump, mock_file):
        """Test saving template data to a file."""
        # Setup test data
        TEMPLATE_DATA["FILES"] = [{"id": "file1"}]

        # Call function
        save_template("/path/to/template.yaml.j2")

        # Verify file was opened for writing
        mock_file.assert_called_once_with(
            "/path/to/template.yaml.j2", "w", encoding="utf-8"
        )

        # Verify yaml.safe_dump was called with the template data
        mock_yaml_dump.assert_called_once()
        args, kwargs = mock_yaml_dump.call_args
        assert args[0] == TEMPLATE_DATA
        assert kwargs["default_flow_style"] is False
        assert kwargs["sort_keys"] is False
