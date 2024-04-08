from typing import List, Union, Any
import re
from swarmauri.core.chunkers.IChunker import IChunker

class DelimiterBasedChunker(IChunker):
    """
    A concrete implementation of IChunker that splits text into chunks based on specified delimiters.
    """

    def __init__(self, delimiters: List[str] = None):
        """
        Initializes the chunker with a list of delimiters.

        Parameters:
        - delimiters (List[str], optional): A list of strings that will be used as delimiters for splitting the text.
                                            If not specified, a default list of sentence-ending punctuation is used.
        """
        if delimiters is None:
            delimiters = ['.', '!', '?']  # Default delimiters
        # Create a regex pattern that matches any of the specified delimiters.
        # The pattern uses re.escape on each delimiter to ensure special regex characters are treated literally.
        self.delimiter_pattern = f"({'|'.join(map(re.escape, delimiters))})"
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Chunks the given text based on the delimiters specified during initialization.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks split based on the specified delimiters.
        """
        # Split the text based on the delimiter pattern, including the delimiters in the result
        chunks = re.split(self.delimiter_pattern, text)
        # Combine delimiters with the preceding text chunk since re.split() separates them
        combined_chunks = []
        for i in range(0, len(chunks) - 1, 2):  # Step by 2 to process text chunk with its following delimiter
            combined_chunks.append(chunks[i] + (chunks[i + 1] if i + 1 < len(chunks) else ''))
        return combined_chunks