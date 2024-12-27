import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from swarmauri.utils.print_notebook_metadata import (
    get_notebook_name,
    print_notebook_metadata,
)


@pytest.fixture
def mock_ipython():
    """Fixture to create a mock IPython environment"""
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
    """Test successful notebook name retrieval"""
    with patch(
        "swarmauri.utils.print_notebook_metadata.get_ipython", return_value=mock_ipython
    ):
        result = get_notebook_name()
        assert result == "test_notebook.ipynb"


def test_get_notebook_name_no_ipython():
    """Test when IPython is not available"""
    with patch("swarmauri.utils.print_notebook_metadata.get_ipython", return_value=None):
        result = get_notebook_name()
        assert result is None


def test_get_notebook_name_invalid_filename():
    """Test with invalid filename format"""
    mock_kernel = Mock()
    mock_parent = {"metadata": {"filename": "invalid_file.txt"}}  # Not an ipynb file
    mock_kernel.get_parent.return_value = mock_parent
    mock_ip = Mock()
    mock_ip.kernel = mock_kernel

    with patch("swarmauri.utils.print_notebook_metadata.get_ipython", return_value=mock_ip):
        result = get_notebook_name()
        assert result is None


def test_get_notebook_name_with_url_parameters():
    """Test filename cleaning from URL parameters"""
    mock_kernel = Mock()
    mock_parent = {"metadata": {"filename": "notebook.ipynb?param=value#fragment"}}
    mock_kernel.get_parent.return_value = mock_parent
    mock_ip = Mock()
    mock_ip.kernel = mock_kernel

    with patch("swarmauri.utils.print_notebook_metadata.get_ipython", return_value=mock_ip):
        result = get_notebook_name()
        assert result == "notebook.ipynb"


@pytest.mark.parametrize("exception_type", [AttributeError, KeyError, Exception])
def test_get_notebook_name_exceptions(exception_type):
    """Test exception handling"""
    with patch("swarmauri.utils.print_notebook_metadata.get_ipython", side_effect=exception_type("Test error")):
        result = get_notebook_name()
        assert result is None


@pytest.fixture
def mock_environment():
    """Fixture to mock environment-dependent functions"""
    mock_datetime = datetime(2024, 1, 1, 12, 0)

    with patch("os.path.getmtime", return_value=mock_datetime.timestamp()), patch(
        "platform.system", return_value="Test OS"
    ), patch("platform.release", return_value="1.0"), patch(
        "sys.version", "3.8.0"
    ), patch(
        "swarmauri.utils.print_notebook_metadata.get_notebook_name", return_value="test_notebook.ipynb"
    ):
        yield mock_datetime


def test_print_notebook_metadata(mock_environment, capsys):
    """Test printing notebook metadata"""
    with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
        print_notebook_metadata("Test Author", "testgithub")

        captured = capsys.readouterr()
        output = captured.out

        assert "Author: Test Author" in output
        assert "GitHub Username: testgithub" in output
        assert "Notebook File: test_notebook.ipynb" in output
        assert "Last Modified: 2024-01-01 12:00:00" in output
        assert "Test OS 1.0" in output
        assert "Python Version: 3.8.0" in output
        assert f"Swarmauri Version: {version('swarmauri')}" in output


def test_print_notebook_metadata_with_swarmauri(mock_environment, capsys):
    """Test printing notebook metadata with Swarmauri installed"""
    with patch("importlib.metadata.version", return_value=version("swarmauri")):
        print_notebook_metadata("Test Author", "testgithub")

        captured = capsys.readouterr()
        output = captured.out

        assert f"Swarmauri Version: {version('swarmauri')}" in output


def test_print_notebook_metadata_no_notebook(capsys):
    """Test printing metadata when notebook name cannot be determined"""
    with patch("swarmauri.utils.print_notebook_metadata.get_notebook_name", return_value=None):
        print_notebook_metadata("Test Author", "testgithub")

        captured = capsys.readouterr()
        output = captured.out

        assert "Could not detect the current notebook's filename" in output
