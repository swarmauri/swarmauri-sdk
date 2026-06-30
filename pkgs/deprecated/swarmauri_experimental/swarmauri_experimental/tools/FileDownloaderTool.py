import httpx
from typing import Dict
from swarmauri.tools.concrete.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter


class FileDownloaderTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the file to download",
                required=True,
            )
        ]

        super().__init__(
            name="FileDownloaderTool",
            description="Downloads a file from a specified URL into memory.",
            parameters=parameters,
        )

    def __call__(self, url: str) -> Dict[str, bytes]:
        """
        Downloads a file from the given URL into memory.

        Parameters:
        - url (str): The URL of the file to download.

        Returns:
        - Dict[str, bytes]: A dictionary containing the file content as bytes.
        """
        try:
            response = httpx.get(url)
            # Raises an HTTPError if the request resulted in an error
            response.raise_for_status()
            return {"file_content": response.content}
        except httpx.HTTPError as e:
            raise RuntimeError(
                f"Failed to download file from '{url}'. Error: {e}"
            )
