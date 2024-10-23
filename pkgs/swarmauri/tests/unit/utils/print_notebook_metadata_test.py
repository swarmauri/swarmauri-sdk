import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from swarmauri.utils.print_notebook_metadata import print_notebook_metadata


@pytest.fixture
def mock_os_functions():
    """Fixture to mock os.path functions for file time metadata"""
    with patch("os.path.getmtime") as mock_getmtime:
        mock_getmtime.return_value = datetime(
            2024, 10, 23, 15, 0, 0
        ).timestamp()  # Set a fixed modification date
        yield mock_getmtime


@pytest.fixture
def mock_get_notebook_name():
    """Fixture to mock the IPython environment and metadata"""
    with patch(
        "swarmauri.utils.print_notebook_metadata.get_notebook_name"
    ) as mock_get_notebook_name:
        mock_get_notebook_name.return_value = "sample_notebook.ipynb"
        yield mock_get_notebook_name


@pytest.fixture
def mock_platform():
    """Fixture to mock platform information"""
    with patch("platform.system") as mock_system, patch(
        "platform.release"
    ) as mock_release:
        mock_system.return_value = "Linux"
        mock_release.return_value = "5.4.0"
        yield mock_system, mock_release


@pytest.fixture
def mock_sys_version():
    """Fixture to mock sys version"""
    with patch("sys.version", "3.9.7 (default, Oct 23 2024, 13:30:00) [GCC 9.3.0]"):
        yield


@pytest.fixture
def mock_swarmauri_import():
    """Fixture to mock swarmauri import check"""
    with patch("builtins.__import__") as mock_import:
        # Mock swarmauri as an available module with a version
        mock_swarmauri = MagicMock()
        mock_swarmauri.__version__ = "1.0.0"
        mock_import.return_value = mock_swarmauri
        yield mock_import


@pytest.fixture
def mock_author_info():
    """Fixture to provide author information"""
    return {"author_name": "Test Author", "github_username": "testuser"}


def test_print_notebook_metadata_without_swarmauri(
    mock_os_functions,
    mock_get_notebook_name,
    mock_platform,
    mock_sys_version,
    mock_author_info,
):
    """Test for print_notebook_metadata without Swarmauri is not installed"""

    # Extract author info from the fixture
    author_name = mock_author_info["author_name"]
    github_username = mock_author_info["github_username"]

    # Mocked print function to capture output
    with patch("builtins.print") as mock_print:
        with patch("builtins.__import__", side_effect=ImportError):
            print_notebook_metadata(author_name, github_username)

        # Check expected calls
        mock_print.assert_any_call(f"Author: {author_name}")
        mock_print.assert_any_call(f"GitHub Username: {github_username}")
        mock_print.assert_any_call(f"Notebook File: sample_notebook.ipynb")
        mock_print.assert_any_call("Last Modified: 2024-10-23 15:00:00")
        mock_print.assert_any_call("Platform: Linux 5.4.0")
        mock_print.assert_any_call(
            "Python Version: 3.9.7 (default, Oct 23 2024, 13:30:00) [GCC 9.3.0]"
        )
        mock_print.assert_any_call("Swarmauri is not installed.")
