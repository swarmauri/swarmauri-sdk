import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from swarmauri_standard.utils.print_notebook_metadata import (
    get_notebook_name,
    print_notebook_metadata,
)


@pytest.fixture
def mock_ipython():
    """Fixture to create a mock IPython environment."""
    mock_kernel = Mock()
    mock_parent = {
        "metadata": {
            "filename": "test_notebook.ipynb",
            "originalPath": "/path/to/test_notebook.ipynb",
            "cellId": "some/path/test_notebook.ipynb",
        }
    }
    mock_kernel.get_parent.return_value = mock_parent

    mock_ip = Mock()
    mock_ip.kernel = mock_kernel
    return mock_ip


def test_get_notebook_name_success(mock_ipython):
    """Test successful notebook name retrieval."""
    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_ipython",
        return_value=mock_ipython,
    ):
        result = get_notebook_name()
        assert result == "test_notebook.ipynb"


def test_get_notebook_name_no_ipython():
    """Test when IPython is not available."""
    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_ipython",
        return_value=None,
    ):
        result = get_notebook_name()
        assert result is None


def test_get_notebook_name_invalid_filename():
    """Test with invalid filename format."""
    mock_kernel = Mock()
    mock_parent = {"metadata": {"filename": "invalid_file.txt"}}  # Not an ipynb file
    mock_kernel.get_parent.return_value = mock_parent
    mock_ip = Mock()
    mock_ip.kernel = mock_kernel

    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_ipython",
        return_value=mock_ip,
    ):
        result = get_notebook_name()
        assert result is None


def test_get_notebook_name_with_url_parameters():
    """Test filename cleaning from URL parameters."""
    mock_kernel = Mock()
    mock_parent = {"metadata": {"filename": "notebook.ipynb?param=value#fragment"}}
    mock_kernel.get_parent.return_value = mock_parent
    mock_ip = Mock()
    mock_ip.kernel = mock_kernel

    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_ipython",
        return_value=mock_ip,
    ):
        result = get_notebook_name()
        assert result == "notebook.ipynb"


@pytest.mark.parametrize("exception_type", [AttributeError, KeyError, Exception])
def test_get_notebook_name_exceptions(exception_type):
    """Test exception handling in get_notebook_name."""
    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_ipython",
        side_effect=exception_type("Test error"),
    ):
        result = get_notebook_name()
        assert result is None


@pytest.fixture
def mock_environment():
    """Fixture to mock environment-dependent functions."""
    # Set a fixed datetime value for modification time
    mock_datetime = datetime(2024, 1, 1, 12, 0)

    with patch("os.path.getmtime", return_value=mock_datetime.timestamp()), patch(
        "platform.system", return_value="Test OS"
    ), patch("platform.release", return_value="1.0"), patch.object(
        sys, "version", "3.8.0"
    ), patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_notebook_name",
        return_value="test_notebook.ipynb",
    ):
        yield mock_datetime


def test_print_notebook_metadata(mock_environment, capsys):
    """Test printing notebook metadata when version information cannot be retrieved from metadata (fallback)."""
    # Patch get_version_from_pyproject to simulate a fallback value.
    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_version_from_pyproject",
        return_value="development",
    ):
        print_notebook_metadata("Test Author", "testgithub")
        captured = capsys.readouterr()
        output = captured.out

        assert "Author: Test Author" in output
        assert "GitHub Username: testgithub" in output
        assert "Notebook File: test_notebook.ipynb" in output
        assert "Last Modified: 2024-01-01 12:00:00" in output
        assert "Test OS 1.0" in output
        assert "Python Version: 3.8.0" in output
        assert "Swarmauri Version: development" in output


def test_print_notebook_metadata_with_swarmauri(mock_environment, capsys):
    """Test printing notebook metadata when a valid version is returned."""
    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_version_from_pyproject",
        return_value="0.1.0",
    ):
        print_notebook_metadata("Test Author", "testgithub")
        captured = capsys.readouterr()
        output = captured.out

        assert "Swarmauri Version: 0.1.0" in output


def test_print_notebook_metadata_no_notebook(capsys):
    """Test printing metadata when the notebook name cannot be determined."""
    with patch(
        "swarmauri_standard.utils.print_notebook_metadata.get_notebook_name",
        return_value=None,
    ):
        print_notebook_metadata("Test Author", "testgithub")
        captured = capsys.readouterr()
        output = captured.out

        assert "Could not detect the current notebook's filename" in output
