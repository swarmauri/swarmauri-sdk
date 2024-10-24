from typing import Any, List, Literal, Union

import pypdftk  # PyPDFTK
from swarmauri.documents.concrete.Document import Document
from swarmauri.parsers.base.ParserBase import ParserBase
from swarmauri_core.documents.IDocument import IDocument


class PyPDFTKParser(ParserBase):
    """
    Parser for reading and extracting data fields from PDF files using PyPDFTK.
    """

    type: Literal["PyPDFTKParser"] = "PyPDFTKParser"

    def parse(self, source: str) -> List[IDocument]:
        """
        Parses a PDF file and extracts its data fields as Document instances.

        Parameters:
        - source (str): The path to the PDF file.

        Returns:
        - List[IDocument]: A list containing a single IDocument instance with the extracted data fields.
        """
        if not isinstance(source, str):
            raise ValueError("PyPDFTKParser expects a file path as a string.")

        try:
            fields = pypdftk.dump_data_fields(source)

            if not fields:
                print(f"No data fields found in the PDF: {source}")
                return []

            fields_str = "\n".join([f"{key}: {value}" for key, value in fields.items()])

            document = Document(content=fields_str, metadata={"source": source})
            return [document]

        except Exception as e:
            print(f"An unexpected error occurred while parsing the PDF '{source}': {e}")
            return []
