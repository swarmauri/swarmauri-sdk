import pdfplumber
from typing import List,Tuple,Literal,Union
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument

class PDFPlumberParser(ParserBase):
    """
    Parser for reading and extracting text from PDF files using PDFPlumber.
    """
    type: Literal["PDFPlumberParser"] = "PDFPlumberParser"

    def parse(self, source: Union[str, bytes]) -> List[IDocument]:
        """
        Parses a PDF file and extracts text from each page as Document instances.

        Parameters:
        - source (Union[str, bytes]): The path to the PDF file or bytes of the PDF content.

        Returns:
        - List[IDocument]: A list of IDocument instances with the extracted text.
        
        """
        documents = []
        
        try:
            if isinstance(source, str):
                with pdfplumber.open(source) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            documents.append(Document(content=text.strip(), metadata={
                                "page_number": page.page_number + 1,
                                "source": source,
                            }))
            elif isinstance(source, bytes):
                from io import BytesIO
                with pdfplumber.open(BytesIO(source)) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            documents.append(Document(content=text.strip(), metadata={
                                "page_number": page.page_number + 1,
                                "source": "bytes",
                            }))
            else:
                raise TypeError("Source must be of type str (file path) or bytes.")
        except Exception as e:
            print(f"An error occurred while parsing the PDF: {e}")
            return []

        return documents