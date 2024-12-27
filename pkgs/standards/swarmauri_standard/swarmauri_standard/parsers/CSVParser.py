import csv
from io import StringIO
from typing import List, Union, Any, Literal
from swarmauri_core.documents.IDocument import IDocument
from swarmauri_standard.documents.Document import Document
from swarmauri_base.parsers.ParserBase import ParserBase

class CSVParser(ParserBase):
    """
    Concrete implementation of IParser for parsing CSV formatted text into Document instances.

    The parser can handle input as a CSV formatted string or from a file, with each row
    represented as a separate Document. Assumes the first row is the header which will
    be used as keys for document metadata.
    """
    type: Literal['CSVParser'] = 'CSVParser'
    
    def parse(self, data: Union[str, Any]) -> List[IDocument]:
        """
        Parses the given CSV data into a list of Document instances.

        Parameters:
        - data (Union[str, Any]): The input data to parse, either as a CSV string or file path.

        Returns:
        - List[IDocument]: A list of documents parsed from the CSV data.
        """
        # Prepare an in-memory string buffer if the data is provided as a string
        if isinstance(data, str):
            data_stream = StringIO(data)
        else:
            raise ValueError("Data provided is not a valid CSV string")

        # Create a list to hold the parsed documents
        documents: List[IDocument] = []

        # Read CSV content row by row
        reader = csv.DictReader(data_stream)
        for row in reader:
            # Each row represents a document, where the column headers are metadata fields
            document = Document(doc_id=row.get('id', None), 
                                        content=row.get('content', ''), 
                                        metadata=row)
            documents.append(document)

        return documents