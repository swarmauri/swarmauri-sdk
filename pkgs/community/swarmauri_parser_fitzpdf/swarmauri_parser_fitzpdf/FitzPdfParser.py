import pymupdf  # PyMuPDF
from typing import List, Union, Any, Literal
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_standard.documents.Document import Document
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParserBase, "FitzPdfParser")
class FitzPdfParser(ParserBase):
    """
    A parser to extract text from PDF files.
    """

    type: Literal["FitzPdfParser"] = "FitzPdfParser"

    def parse(self, data: Union[str, Any]) -> List[Document]:
        """
        Parses a PDF file and extracts its text content as Document instances.

        Parameters:
        - data (Union[str, Any]): The path to the PDF file.

        Returns:
        - List[IDocument]: A list with a single IDocument instance containing the extracted text.
        """
        # Ensure data is a valid str path to a PDF file
        if not isinstance(data, str):
            raise ValueError("PDFtoTextParser expects a file path in str format.")

        try:
            # Open the PDF file
            doc = pymupdf.open(data)
            text = ""

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            # Create a document with the extracted text
            document = Document(content=text, metadata={"source": data})
            return [document]

        except Exception as e:
            print(f"An error occurred while parsing the PDF: {e}")
            return []
