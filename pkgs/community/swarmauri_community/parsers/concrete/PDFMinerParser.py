from typing import Any, List, Literal, Union

from pdfminer.high_level import extract_text
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument

class PDFMinerParser(ParserBase):
    """
    Parser for reading and extracting text from PDF files using PDFMiner.
    """

    type: Literal["PDFMinerParser"] = "PDFMinerParser"

    def parse(self, source: Union[str, bytes]) -> List[IDocument]:
        """
        Parses a PDF file and extracts text from each page as Document instances.

        Parameters:
        - source (Union[str, bytes]): The path to the PDF file or bytes of the PDF content.

        Returns:
        - List[IDocument]: A list of IDocument instances with the extracted text.
        """

        if isinstance(source, str):
            try:
                text = extract_text(source)
                if text:
                    document = Document(
                        content=text,
                        metadata={"source": source},
                    )
                return [document]
            except Exception as e:
                print(f"An error occurred while parsing the PDF '{source}': {e}")
                return []
        elif isinstance(source, bytes):
            try:
                from io import BytesIO

                file_stream = BytesIO(source)
                text = extract_text(file_stream)
                if text:
                    document = Document(
                        content=text,
                        metadata={"source": "bytes"},
                    )
                return [document]

            except Exception as e:
                print(f"An error occurred while parsing the PDF from bytes: {e}")
                return []