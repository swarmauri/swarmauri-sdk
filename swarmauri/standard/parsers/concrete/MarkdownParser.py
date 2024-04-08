import re
from markdown import markdown
from bs4 import BeautifulSoup
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.Document import Document

class MarkdownParser(IParser):
    """
    A concrete implementation of the IParser interface that parses Markdown text.
    
    This parser takes Markdown formatted text, converts it to HTML using Python's
    markdown library, and then uses BeautifulSoup to extract plain text content. The
    resulting plain text is then wrapped into IDocument instances.
    """
    
    def parse(self, data: str) -> list[IDocument]:
        """
        Parses the input Markdown data into a list of IDocument instances.
        
        Parameters:
        - data (str): The input Markdown formatted text to be parsed.
        
        Returns:
        - list[IDocument]: A list containing a single IDocument instance with the parsed text content.
        """
        # Convert Markdown to HTML
        html_content = markdown(data)
        
        # Use BeautifulSoup to extract text content from HTML
        soup = BeautifulSoup(html_content, features="html.parser")
        plain_text = soup.get_text(separator=" ", strip=True)
        
        # Generate a document ID
        doc_id = "1"  # For this implementation, a simple fixed ID is used. 
                      # A more complex system might generate unique IDs for each piece of text.

        # Create and return a list containing the single extracted plain text document
        document = Document(doc_id=doc_id, content=plain_text, metadata={"source_format": "markdown"})
        return [document]