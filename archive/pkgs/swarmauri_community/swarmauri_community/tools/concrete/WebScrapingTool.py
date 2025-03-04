import requests
from bs4 import BeautifulSoup
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
from typing import List, Literal, Dict
from pydantic import Field


class WebScrapingTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="url",
                type="string",
                description="URL of the link, website, webpage, etc... to scrape",
                required=True,
            ),
            Parameter(
                name="selector",
                type="string",
                description="CSS selector to target specific elements",
                required=True,
            ),
        ]
    )

    name: str = "WebScrapingTool"
    description: str = (
        "This is a web scraping tool that uses python's requests and BeautifulSoup libraries to parse a URL using a CSS selector to target specific elements."
    )
    type: Literal["WebScrapingTool"] = "WebScrapingTool"

    def __call__(self, url: str, selector: str) -> Dict[str, str]:
        """
        Fetches content from the specified URL and extracts elements based on the provided CSS selector.

        Args:
            url (str): The URL of the webpage to scrape.
            selector (str): CSS selector to target specific elements in the webpage.

        Returns:
            Dict: A dictionary containing the extracted text or an error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad requests (4xx or 5xx)

            html_content = response.content
            soup = BeautifulSoup(html_content, "html.parser")

            elements = soup.select(selector)
            extracted_text = "\n".join([element.text for element in elements])
            return {"extracted_text": extracted_text}
        except requests.RequestException as e:
            return {"error": f"Request error: {str(e)}"}
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
