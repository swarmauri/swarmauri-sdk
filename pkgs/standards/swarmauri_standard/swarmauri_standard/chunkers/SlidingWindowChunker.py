from typing import List, Literal
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase


class SlidingWindowChunker(ChunkerBase):
    """
    A concrete implementation of ChunkerBase that uses sliding window technique
    to break the text into chunks.
    """
    window_size: int = 256
    step_size: int = 256
    overlap: bool = False
    type: Literal['SlidingWindowChunker'] = 'SlidingWindowChunker'
         
    def chunk_text(self, text: str, *args, **kwargs) -> List[str]:
        """
        Splits the input text into chunks based on the sliding window technique.
        
        Parameters:
        - text (str): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        step_size = self.step_size if self.overlap else self.window_size  # Non-overlapping if window size equals step size.


        words = text.split()  # Tokenization by whitespaces. More sophisticated tokenization might be necessary.
        chunks = []
        
        for i in range(0, len(words) - self.window_size + 1, step_size):
            chunk = ' '.join(words[i:i+self.window_size])
            chunks.append(chunk)
        
        return chunks