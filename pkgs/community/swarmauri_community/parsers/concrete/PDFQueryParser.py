from typing import List, Literal, Union
import pdfquery
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument
from io import BytesIO

class PDFQueryParser(ParserBase):
    """
    Parser for reading and extracting text from PDF files using PDFQuery.
    """
    type: Literal["PDFQueryParser"] = "PDFQueryParser"

    def parse(self, source: Union[str, bytes]) -> List[IDocument]:
        """
        Parses a PDF file and extracts text from each page as Document instances.

        Parameters:
        - source (Union[str, bytes]): The path to the PDF file or bytes of the PDF content.

        Returns:
        - List[IDocument]: A list of IDocument instances with the extracted text.
        """
        documents = []

        if isinstance(source, str):
            # Handle file path
            try:
                pdf = pdfquery.PDFQuery(source)
                pdf.load()
                text = pdf.tree.text_content().strip()
                documents.append(Document(content=text, metadata={"source": source}))
            except Exception as e:
                print(f"An error occurred while parsing the PDF '{source}': {e}")
                return []

        elif isinstance(source, bytes):
            # Handle bytes content
            try:
                file_stream = BytesIO(source)
                pdf = pdfquery.PDFQuery(file_stream)
                pdf.load()
                text = pdf.tree.text_content().strip()
                documents.append(Document(content=text, metadata={"source": "bytes"}))
            except Exception as e:
                print("An error occurred while parsing the PDF from bytes:", e)
                return []

        else:
            raise TypeError("Source must be of type str (file path) or bytes.")

        return documents