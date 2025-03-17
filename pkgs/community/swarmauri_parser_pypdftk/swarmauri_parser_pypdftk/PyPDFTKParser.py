from typing import List, Literal

import pypdftk
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParserBase, "PyPDFTKParser")
class PyPDFTKParser(ParserBase):
    """
    Parser for reading and extracting data fields from PDF files using PyPDFTK.
    """

    type: Literal["PyPDFTKParser"] = "PyPDFTKParser"

    def parse(self, source: str) -> List[Document]:
        """
        Parses a PDF file and extracts its data fields as Document instances.

        Parameters:
        - source (str): The path to the PDF file.

        Returns:
        - List[IDocument]: A list containing a single Document instance with the extracted data fields.
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
