from typing import List, Union, Any, Literal
import re
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase

class DelimiterBasedChunker(ChunkerBase):
    """
    A concrete implementation of IChunker that splits text into chunks based on specified delimiters.
    """
    version: str = "0.1.0.dev13"
    delimiters: List[str] = ['.', '!', '?']
    type: Literal['DelimiterBasedChunker'] = 'DelimiterBasedChunker'
    
    def chunk_text(self, text: Union[str, Any], *args, **kwargs) -> List[str]:
        """
        Chunks the given text based on the delimiters specified during initialization.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks split based on the specified delimiters.
        """
        delimiter_pattern = f"({'|'.join(map(re.escape, self.delimiters))})"
        
        # Split the text based on the delimiter pattern, including the delimiters in the result
        chunks = re.split(delimiter_pattern, text)
        
        # Combine delimiters with the preceding text chunk since re.split() separates them
        combined_chunks = []
        for i in range(0, len(chunks), 2):  # Step by 2 to process text chunk with its following delimiter
            combined_chunks.append(chunks[i] + (chunks[i + 1] if i + 1 < len(chunks) else ''))

        # Remove whitespace
        combined_chunks = [chunk.strip() for chunk in combined_chunks]
        return combined_chunks
