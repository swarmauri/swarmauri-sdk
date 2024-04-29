import requests
from bs4 import BeautifulSoup
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class WebScrapingTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="url",
                type="string",
                description="URL of the link, website, webpage, etc... to scrape",
                required=True
            ),
            Parameter(
                name="selector",
                type="string",
                description="CSS selector to target specific elements",
                required=True
            )
        ]
        
        super().__init__(name="WebScrapingTool", 
                         description="This is a web scraping tool that you can utilize to scrape links, websites, webpages, etc... This tool uses python's requests and BeautifulSoup libraries to parse a URL using a CSS to target specific elements.", 
                         parameters=parameters)

    def __call__(self, url: str, selector: str) -> str:
        """
        Fetches content from the specified URL and extracts elements based on the provided CSS selector.
        
        Args:
            url (str): The URL of the webpage to scrape.
            selector (str): CSS selector to target specific elements in the webpage.

        Returns:
            str: Extracted text from the selector or an error message.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises HTTPError for bad requests (4xx or 5xx)

            html_content = response.content
            soup = BeautifulSoup(html_content, 'html.parser')

            elements = soup.select(selector)
            extracted_text = '\n'.join([element.text for element in elements])
            return extracted_text
        except requests.RequestException as e:
            return f"Request Exception: {str(e)}"
        except Exception as e:
            return f"Unexpected error: {str(e)}"