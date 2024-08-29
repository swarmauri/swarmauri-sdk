# Import necessary modules
import requests
from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, Extra
from swarmauri.standard.tools.base.ToolBase import ToolBase  # Assuming the location of ToolBase import

class RequestsTool(ToolBase):
    """
    A tool that leverages the `requests` library to perform HTTP operations.

    Attributes:
        name (str): The name of the tool.
        description (str): A brief description of what the tool does.
    """
    name: Literal['RequestsTool'] = 'RequestsTool'
    description: Optional[str] = "A tool for making HTTP requests using the `requests` library."

    class Config:
        extra = Extra.forbid

    def get(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Perform an HTTP GET request.

        Args:
            url (str): The URL to send the GET request to.
            params (Optional[Dict[str, Any]]): The query parameters to include in the request.
            headers (Optional[Dict[str, str]]): Additional headers to include in the request.

        Returns:
            requests.Response: The response object from the GET request.
        """
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Perform an HTTP POST request.

        Args:
            url (str): The URL to send the POST request to.
            data (Optional[Dict[str, Any]]): The form data to include in the request.
            json (Optional[Dict[str, Any]]): The JSON data to include in the request.
            headers (Optional[Dict[str, str]]): Additional headers to include in the request.

        Returns:
            requests.Response: The response object from the POST request.
        """
        response = requests.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response

    def put(self, url: str, data: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Perform an HTTP PUT request.

        Args:
            url (str): The URL to send the PUT request to.
            data (Optional[Dict[str, Any]]): The form data to include in the request.
            json (Optional[Dict[str, Any]]): The JSON data to include in the request.
            headers (Optional[Dict[str, str]]): Additional headers to include in the request.

        Returns:
            requests.Response: The response object from the PUT request.
        """
        response = requests.put(url, data=data, json=json, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response

    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        Perform an HTTP DELETE request.

        Args:
            url (str): The URL to send the DELETE request to.
            headers (Optional[Dict[str, str]]): Additional headers to include in the request.

        Returns:
            requests.Response: The response object from the DELETE request.
        """
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        return response

    def __call__(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Calls the appropriate HTTP method (GET, POST, PUT, DELETE) based on the method argument.

        Args:
            method (str): The HTTP method to use ('get', 'post', 'put', 'delete').
            url (str): The URL for the request.
            **kwargs: Additional keyword arguments passed to the respective method.

        Returns:
            requests.Response: The response object from the HTTP request.
        """
        method = method.lower()
        if method == 'get':
            return self.get(url, **kwargs)
        elif method == 'post':
            return self.post(url, **kwargs)
        elif method == 'put':
            return self.put(url, **kwargs)
        elif method == 'delete':
            return self.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    def __str__(self):
        return f"{self.name}: {self.description}"
