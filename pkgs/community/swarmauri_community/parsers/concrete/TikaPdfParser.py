from typing import Any, List, Literal, Union
from tika import parser as tika_parser
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument
import os


class TikaPDFParser(ParserBase):
    """
    Parser for reading and extracting content and metadata from PDF files using Apache Tika.
    Provides more robust parsing capabilities compared to PyPDFTK, including text extraction
    and metadata handling.
    """

    type: Literal["TikaPDFParser"] = "TikaPDFParser"

    def parse(self, source: str) -> List[IDocument]:
        """
        Parses a PDF file and extracts its content and metadata as Document instances.

        Parameters:
        - source (str): The path to the PDF file.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with the extracted content
                          and metadata.

        Raises:
        - ValueError: If the source is not a string or the file doesn't exist.
        - Exception: For other parsing errors.
        """
        if not isinstance(source, str):
            raise ValueError("TikaPDFParser expects a file path as a string.")

        if not os.path.exists(source):
            raise ValueError(f"File not found: {source}")

        try:
            # Parse PDF using Tika
            parsed_pdf = tika_parser.from_file(source)

            if not parsed_pdf:
                print(f"No content could be extracted from the PDF: {source}")
                return []

            # Extract content and metadata
            content = parsed_pdf.get("content", "").strip()
            metadata = parsed_pdf.get("metadata", {})
            
            # Create document instance
            document = Document(content=content, metadata=metadata)

            return [document]

        except Exception as e:
            print(f"An error occurred while parsing the PDF '{source}': {str(e)}")
            return []

    