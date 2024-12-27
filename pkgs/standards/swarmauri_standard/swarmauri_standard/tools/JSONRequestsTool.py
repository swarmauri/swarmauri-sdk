from swarmauri_core.typing import SubclassUnion

# Import necessary modules
import requests
from typing import Optional, Dict, Any, Literal, List
from pydantic import Field
from swarmauri.tools.base.ToolBase import (
    ToolBase,
)  # Assuming the location of ToolBase import
from swarmauri_standard.tools.Parameter import Parameter


class JSONRequestsTool(ToolBase):
    """
    A tool that leverages the `requests` library to perform HTTP operations.

    Attributes:
        name (str): The name of the tool.
        description (str): A brief description of what the tool does.
    """

    name: str = "JSONRequestsTool"
    type: Literal["JSONRequestsTool"] = "JSONRequestsTool"
    description: Optional[str] = (
        "A tool for making HTTP requests using the `requests` library."
    )
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="method",
                type="string",
                description="The HTTP method to use ('get', 'post', 'put', 'delete').",
                required=True,
                enum=["get", "post", "put", "delete"],
            ),
            Parameter(
                name="url",
                type="string",
                description="The URL for the request.",
                required=True,
            ),
            Parameter(
                name="params",
                type="object",
                description="The query parameters to include in the request.",
                required=False,
            ),
            Parameter(
                name="data",
                type="object",
                description="The form data to include in the request (used in POST and PUT).",
                required=False,
            ),
            Parameter(
                name="json",
                type="object",
                description="The JSON data to include in the request (used in POST and PUT).",
                required=False,
            ),
            Parameter(
                name="headers",
                type="object",
                description="Additional headers to include in the request.",
                required=False,
            ),
        ]
    )

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
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

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
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

    def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
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

    def delete(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
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

    def __call__(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
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
        if method == "get":
            response = self.get(url, **kwargs)
        elif method == "post":
            response = self.post(url, **kwargs)
        elif method == "put":
            response = self.put(url, **kwargs)
        elif method == "delete":
            response = self.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            # If JSON parsing fails, return the raw text and some metadata
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
            }


SubclassUnion.update(
    baseclass=ToolBase, type_name="JSONRequestsTool", obj=JSONRequestsTool
)
