import base64
from io import BytesIO
import requests
from typing import Dict, Literal, List
from pathlib import Path
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter

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
    
    def __call__(self, url: str) -> Dict[str, str]:
        """
        Download the PDF from the specified URL and encode it in base64.

        Parameters:
        - url (str): The URL from where to download the PDF.
        
        Returns:
        - Dict[str, str]: A dictionary containing the result message and the base64 encoded content.
        """
        try:
            # Send a GET request to the specified URL
            response = requests.get(url, stream=True)

            # Raise an HTTPError if the status code is not 200 (OK)
            response.raise_for_status()

            # Read PDF content into memory
            pdf_content = BytesIO()
            for chunk in response.iter_content(chunk_size=8192):
                pdf_content.write(chunk)
                
            pdf_content.seek(0)
            # Encode the PDF content in base64
            encoded_pdf = base64.b64encode(pdf_content.read()).decode('utf-8')

            return {
                "message": "PDF downloaded and encoded successfully.",
                "content": encoded_pdf
            }

        except requests.exceptions.RequestException as e:
            # Handle requests-related errors
            return {"error": f"Failed to download PDF: {e}"}

        except IOError as e:
            # Handle data I/O errors
            return {"error": f"Failed to process PDF: {e}"}