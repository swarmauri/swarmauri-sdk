from typing import List
from swarmauri.core.chunkers.IChunker import IChunker

class SlidingWindowChunker(IChunker):
    """
    A concrete implementation of IChunker that uses sliding window technique
    to break the text into chunks.
    """
    
    def __init__(self, window_size: int, step_size: int, overlap: bool = True):
        """
        Initialize the SlidingWindowChunker with specific window and step sizes.
        
        Parameters:
        - window_size (int): The size of the window for each chunk (in terms of number of words).
        - step_size (int): The step size for the sliding window (in terms of number of words).
        - overlap (bool, optional): Whether the windows should overlap. Default is True.
        """
        self.window_size = window_size
        self.step_size = step_size if overlap else window_size  # Non-overlapping if window size equals step size.
           
    def chunk_text(self, text: str, *args, **kwargs) -> List[str]:
        """
        Splits the input text into chunks based on the sliding window technique.
        
        Parameters:
        - text (str): The input text to be chunked.
        
        Returns:
        - List[str]: A list of text chunks.
        """
        words = text.split()  # Tokenization by whitespaces. More sophisticated tokenization might be necessary.
        chunks = []
        
        for i in range(0, len(words) - self.window_size + 1, self.step_size):
            chunk = ' '.join(words[i:i+self.window_size])
            chunks.append(chunk)
        
        return chunks