from typing import List, Literal

import slate3k as slate
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParserBase, "SlateParser")
class SlateParser(ParserBase):
    """
    Parser for reading and extracting data fields from PDF files using Slate3k.
    """

    type: Literal["SlateParser"] = "SlateParser"

    def parse(self, source: str) -> List[Document]:
        """
        Parses a PDF file and extracts its data fields as Document instances.

        Parameters:
        - source (str): The path to the PDF file.

        Returns:
        - List[IDocument]: A list containing a single Document instance with the extracted data fields.
        """

        documents = []
        if isinstance(source, str):
            try:
                with open(source, "rb") as file:
                    reader = slate.PDF(file)
                    print(reader)
                    for page_num, page in enumerate(reader):
                        text = page
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
        else:
            raise TypeError("Source must be of type str (file path) or bytes.")

        return documents
