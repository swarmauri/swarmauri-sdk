import pytest
from swarmauri_standard.dataconnectors.GoogleDriveDataConnector import (
    GoogleDriveDataConnector,
)


@pytest.fixture(scope="module")
def authenticated_connector():
    """Authenticate the GoogleDriveDataConnector once for the test suite."""
    # Path to the valid credentials JSON file
    credentials_path = "pkgs/swarmauri_standard/tests/static/credentials.json"
    connector = GoogleDriveDataConnector(credentials_path=credentials_path)

    # Perform authentication once
    try:
        connector.authenticate()  # Requires manual input for the authorization code
    except Exception as e:
        pytest.fail(f"Authentication failed: {e}")

    return connector


@pytest.fixture(scope="module")
def shared_file_id():
    """Return a shared file ID for testing."""
    return {}


@pytest.mark.skip(reason="Skipping test_generate_authorization_url")
def test_generate_authorization_url():
    """Test generate_authorization_url without authentication."""
    # Path to the valid credentials JSON file
    credentials_path = "pkgs/swarmauri_standard/tests/static/credentials.json"
    connector = GoogleDriveDataConnector(credentials_path=credentials_path)
    url = connector.generate_authorization_url()
    assert isinstance(url, str)
    assert "client_id" in url
    assert "redirect_uri" in url
    assert "https://accounts.google.com/o/oauth2/v2/auth" in url


@pytest.mark.skip(reason="Skipping test_fetch_data")
def test_fetch_data(authenticated_connector):
    """Test fetching data from Google Drive."""
    documents = authenticated_connector.fetch_data(query="test")
    assert isinstance(documents, list)
    if documents:
        assert all(hasattr(doc, "content") for doc in documents)
        assert all(hasattr(doc, "metadata") for doc in documents)


@pytest.mark.skip(reason="Skipping test_insert_data")
def test_insert_data(authenticated_connector, shared_file_id):
    """Test inserting data into Google Drive."""
    test_data = "Sample content for Google Drive file"
    file_id = authenticated_connector.insert_data(test_data, filename="test_file.txt")
    assert isinstance(file_id, str)
    shared_file_id["file_id"] = file_id


@pytest.mark.skip(reason="Skipping test_update_data")
def test_update_data(authenticated_connector, shared_file_id):
    """Test updating data in Google Drive."""
    file_id = shared_file_id["file_id"]
    updated_content = "Updated content for Google Drive file"
    try:
        authenticated_connector.update_data(file_id, updated_content)
    except Exception as e:
        pytest.fail(f"Failed to update file: {e}")


@pytest.mark.skip(reason="Skipping test_delete_data")
def test_delete_data(authenticated_connector, shared_file_id):
    """Test deleting data from Google Drive."""
    file_id = shared_file_id["file_id"]  # Replace with an actual file ID
    try:
        authenticated_connector.delete_data(file_id)
    except Exception as e:
        pytest.fail(f"Failed to delete file: {e}")


@pytest.mark.skip(reason="Skipping test_connection")
def test_connection(authenticated_connector):
    """Test the connection to Google Drive."""
    connection_success = authenticated_connector.test_connection()
    assert connection_success is True
