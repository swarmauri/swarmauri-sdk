import logging
from urllib.parse import urlencode
import httpx
import base64
import json
from typing import List
from swarmauri_base.documents.DocumentBase import DocumentBase
from swarmauri_base.dataconnectors.DataConnectorBase import DataConnectorBase


class GoogleDriveDataConnector(DataConnectorBase):
    """
    Data connector for interacting with Google Drive files and converting them to Swarmauri documents.

    Supports authentication, data fetching, and basic CRUD operations for Google Drive resources.
    """

    def __init__(self, credentials_path: str = None):
        """
        Initialize the Google Drive Data Connector.

        :param credentials_path: Path to the Google OAuth2 credentials JSON file
        """
        with open(credentials_path, "r") as cred_file:
            credentials = json.load(cred_file)

        self.client_id = credentials.get("client_id")
        self.client_secret = credentials.get("client_secret")
        self.redirect_uri = credentials.get("redirect_uri")

        # Tokens will be stored here
        self.access_token = None
        self.refresh_token = None

        self.authorization_code = None

        self.client = httpx.Client()

    def generate_authorization_url(self) -> str:
        """Generate the authorization URL for user consent"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/drive",
            "access_type": "offline",  # This ensures we get a refresh token
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    def _exchange_code_for_tokens(self):
        """Exchange authorization code for access and refresh tokens"""
        if not self.authorization_code:
            raise ValueError("No authorization code available")

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": self.authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        response = self.client.post(token_url, data=payload)
        tokens = response.json()

        logging.info(f"Token response: {tokens}")
        if "access_token" not in tokens:
            raise ValueError("Failed to obtain access token")
        self.access_token = tokens["access_token"]
        self.refresh_token = tokens.get("refresh_token")

    def refresh_access_token(self):
        """Refresh the access token using the refresh token"""
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }

        response = self.client.post(token_url, data=payload)
        tokens = response.json()
        self.access_token = tokens["access_token"]

    def authenticate(self):
        """
        Authenticate with Google Drive using OAuth2.

        This method generates an authorization URL, prompts the user to visit the URL
        and enter the authorization code, and then exchanges the code for tokens.
        """
        try:
            # Generate authorization URL
            auth_url = self.generate_authorization_url()
            print("Please visit the following URL to authenticate:")
            print(auth_url)

            # Prompt for authorization code
            while True:
                authorization_code = input("Enter the authorization code: ").strip()

                if not authorization_code:
                    print("Authorization code cannot be empty. Please try again.")
                    continue

                self.authorization_code = authorization_code

                try:
                    self._exchange_code_for_tokens()
                    logging.info("Successfully authenticated and obtained tokens")
                    return
                except ValueError as e:
                    print(f"Error exchanging authorization code: {e}")
                    print("Please try again.")
                    self.authorization_code = None

        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            raise ValueError(f"Authentication failed: {e}")

    def fetch_data(self, query: str = None, **kwargs) -> List[DocumentBase]:
        """
        Fetch documents from Google Drive based on a query.

        :param query: Search query for files (optional)
        :param kwargs: Additional parameters like mime_type, max_results
        :return: List of Swarmauri Documents
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            # Prepare request parameters
            query_str = query or ""
            mime_type = kwargs.get("mime_type", "application/vnd.google-apps.document")
            max_results = kwargs.get("max_results", 100)

            # Construct request headers and parameters
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
            }

            params = {
                "q": f"mimeType='{mime_type}' and name contains '{query_str}'",
                "pageSize": max_results,
                "fields": "files(id,name,mimeType)",
            }

            # Make request to Google Drive API
            response = self.client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params=params,
            )
            response.raise_for_status()

            files = response.json().get("files", [])

            # Convert Google Drive files to Swarmauri Documents
            documents = []
            for file in files:
                content = self._get_file_content(file["id"])
                document = DocumentBase(
                    content=content,
                    metadata={
                        "id": file["id"],
                        "name": file["name"],
                        "mime_type": file["mimeType"],
                    },
                )
                documents.append(document)

            return documents

        except httpx.HTTPError as error:
            raise ValueError(f"Error fetching Google Drive files: {error}")

    def _get_file_content(self, file_id: str) -> str:
        """
        Retrieve text content from a Google Drive file.

        :param file_id: ID of the Google Drive file
        :return: Text content of the file
        """
        try:
            # Prepare export request
            headers = {"Authorization": f"Bearer {self.access_token}"}

            # Export file as plain text
            export_url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export"
            params = {"mimeType": "text/plain"}

            response = self.client.get(export_url, headers=headers, params=params)
            response.raise_for_status()

            return response.text

        except httpx.HTTPError as error:
            print(f"An error occurred retrieving file content: {error}")
            return ""

    def insert_data(self, data, **kwargs):
        """
        Insert a new file into Google Drive.

        :param data: Content of the file to be inserted
        :param kwargs: Additional metadata like filename, mime_type
        :return: ID of the inserted file
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            # Prepare file metadata
            file_metadata = {
                "name": kwargs.get("filename", "Untitled Document"),
                "mimeType": kwargs.get(
                    "mime_type", "application/vnd.google-apps.document"
                ),
            }

            # Prepare file content (base64 encoded)
            media_content = base64.b64encode(data.encode("utf-8")).decode("utf-8")

            # Construct payload
            payload = {
                "metadata": file_metadata,
                "media": {"mimeType": "text/plain", "body": media_content},
            }

            # Make request to create file
            response = self.client.post(
                "https://www.googleapis.com/upload/drive/v3/files",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            return response.json().get("id")

        except httpx.HTTPError as error:
            raise ValueError(f"Error inserting file: {error}")

    def update_data(self, identifier, data, **kwargs):
        """
        Update an existing Google Drive file.

        :param identifier: File ID to update
        :param data: New content for the file
        :param kwargs: Additional update parameters
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            # Prepare file content (base64 encoded)
            media_content = base64.b64encode(data.encode("utf-8")).decode("utf-8")

            # Construct payload
            payload = {"media": {"mimeType": "text/plain", "body": media_content}}

            # Make request to update file
            response = self.client.patch(
                f"https://www.googleapis.com/upload/drive/v3/files/{identifier}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        except httpx.HTTPError as error:
            raise ValueError(f"Error updating file: {error}")

    def delete_data(self, identifier, **kwargs):
        """
        Delete a file from Google Drive.

        :param identifier: File ID to delete
        """
        if not self.access_token:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}

            response = self.client.delete(
                f"https://www.googleapis.com/drive/v3/files/{identifier}",
                headers=headers,
            )
            response.raise_for_status()

        except httpx.HTTPError as error:
            raise ValueError(f"Error deleting file: {error}")

    def test_connection(self, **kwargs):
        """
        Test the connection to Google Drive by listing files.

        :return: Boolean indicating connection success
        """
        try:
            if not self.access_token:
                self.authenticate(**kwargs)

            # Prepare request headers
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/json",
            }

            # List first 5 files to test connection
            params = {"pageSize": 5, "fields": "files(id,name)"}

            response = self.client.get(
                "https://www.googleapis.com/drive/v3/files",
                headers=headers,
                params=params,
            )
            response.raise_for_status()

            files = response.json().get("files", [])
            return len(files) > 0

        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
