import requests
from swarmauri.standard.tools.concrete.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter


class FileDownloaderTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="The URL of the file to download",
                required=True
            )
        ]
        
        super().__init__(name="FileDownloaderTool",
                         description="Downloads a file from a specified URL into memory.",
                         parameters=parameters)
    
    def __call__(self, url: str) -> bytes:
        """
        Downloads a file from the given URL into memory.
        
        Parameters:
        - url (str): The URL of the file to download.
        
        Returns:
        - bytes: The content of the downloaded file.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError if the request resulted in an error
            return response.content
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download file from '{url}'. Error: {e}")