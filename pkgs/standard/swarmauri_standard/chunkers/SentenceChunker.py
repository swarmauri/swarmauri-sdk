from typing import Literal
import re
from swarmauri_base.chunkers.ChunkerBase import ChunkerBase

class SentenceChunker(ChunkerBase):
    """
    A simple implementation of the ChunkerBase to chunk text into sentences.
    
    This class uses basic punctuation marks (., !, and ?) as indicators for sentence boundaries.
    """
    type: Literal['SentenceChunker'] = 'SentenceChunker'
    
    def chunk_text(self, text, *args, **kwargs):
        """
        Chunks the given text into sentences using basic punctuation.

        Args:
            text (str): The input text to be chunked into sentences.
        
        Returns:
            List[str]: A list of sentence chunks.
        """
        # Split text using a simple regex pattern that looks for periods, exclamation marks, or question marks.
        # Note: This is a very simple approach and might not work well with abbreviations or other edge cases.
        sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out any empty strings that may have resulted from the split operation
        sentences = [sentence.strip() for sentence in sentences if sentence]
        
        return sentences