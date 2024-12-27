from typing import Any, List, Literal, Union

import PyPDF2 
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument


class PyPDF2Parser(ParserBase):
    """
    Parser for reading and extracting text from PDF files using PyPDF2.
    """

    type: Literal["PyPDF2Parser"] = "PyPDF2Parser"

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
            try:
                with open(source, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for page_num, page in enumerate(reader.pages):
                        text = page.extract_text()
                        if text:
                            document = Document(
                                content=text.strip(),
                                metadata={
                                    "page_number": page_num + 1,
                                    "source": source,
                                },
                            )
                            documents.append(document)
            except Exception as e:
                print(f"An error occurred while parsing the PDF '{source}': {e}")
                return []
        elif isinstance(source, bytes):
            try:
                from io import BytesIO

                file_stream = BytesIO(source)
                reader = PyPDF2.PdfReader(file_stream)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        document = Document(
                            content=text.strip(),
                            metadata={"page_number": page_num + 1, "source": "bytes"},
                        )
                        documents.append(document)
            except Exception as e:
                print("An error occurred while parsing the PDF from bytes:", e)
                return []
        else:
            raise TypeError("Source must be of type str (file path) or bytes.")

        return documents
