import requests
from typing import Dict, Literal, List
from pathlib import Path
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class DownloadPDFTool(ToolBase):
    """
    A tool to download a PDF from a specified URL and save it to a specified path.
    """

    name: str = "DownloadPDFTool"
    description: str = "Downloads a PDF from a specified URL and saves it to a specified path."
    parameters: List[Parameter] = [
        Parameter(
            name="url",
            type="string",
            description="The URL of the PDF file to download",
            required=True
        ),
        Parameter(
            name="destination",
            type="string",
            description="The path where the PDF file will be saved",
            required=True
        )
    ]
    type: Literal['DownloadPDFTool'] = 'DownloadPDFTool'
    
    def __call__(self, url: str, destination: str) -> Dict[str, str]:
        """
        Download the PDF from the specified URL and saves it to the given destination path.

        Parameters:
        - url (str): The URL from where to download the PDF.
        - destination (str): The local file path where the PDF should be saved.
        
        Returns:
        - Dict[str, str]: A dictionary containing the result message and the destination path.
        """
        try:
            # Send a GET request to the specified URL
            response = requests.get(url, stream=True)

            # Raise an HTTPError if the status code is not 200 (OK)
            response.raise_for_status()

            # Ensure destination directory exists
            Path(destination).parent.mkdir(parents=True, exist_ok=True)

            # Open a file at the specified destination path and write the content of the response to it
            with open(Path(destination), 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            return {
                "message": "PDF downloaded successfully.",
                "destination": destination
            }

        except requests.exceptions.RequestException as e:
            # Handle requests-related errors
            return {"error": f"Failed to download PDF: {e}"}
        except IOError as e:
            # Handle file I/O errors
            return {"error": f"Failed to save PDF: {e}"}