import fitz  # PyMuPDF
from typing import List, Union, Any
from ....core.parsers.IParser import IParser
from ....core.documents.IDocument import IDocument
from ....standard.documents.concrete.ConcreteDocument import ConcreteDocument

class PDFtoTextParser(IParser):
    """
    A parser to extract text from PDF files.
    """

    def parse(self, data: Union[str, Any]) -> List[IDocument]:
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
            doc = fitz.open(data)
            text = ""

            # Extract text from each page
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()

            # Create a document with the extracted text
            document = ConcreteDocument(doc_id=str(hash(data)), content=text, metadata={"source": data})
            return [document]
        
        except Exception as e:
            print(f"An error occurred while parsing the PDF: {e}")
            return []
