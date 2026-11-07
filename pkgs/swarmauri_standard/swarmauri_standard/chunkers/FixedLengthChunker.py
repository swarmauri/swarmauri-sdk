from typing import Any, List, Literal

from pydantic import field_validator

from swarmauri_base.chunkers.ChunkerBase import ChunkerBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ChunkerBase, "FixedLengthChunker")
class FixedLengthChunker(ChunkerBase):
    """
    Concrete implementation of ChunkerBase that divides text into fixed-length
    chunks.

    This chunker breaks the input text into chunks of a specified size, making
    sure
    that each chunk has exactly the number of characters specified by the chunk
    size,
    except for possibly the last chunk.
    """

    chunk_size: int = 256
    type: Literal["FixedLengthChunker"] = "FixedLengthChunker"

    @field_validator("chunk_size")
    def validate_chunk_size(cls, v):
        """
        Validate that the chunk size is a positive integer.

        Parameters
        ----------
        v : int
            The chunk size to validate.

        Returns
        -------
        int
            The validated chunk size.

        Raises
        ------
        ValueError
            If the chunk size is zero or negative.
        """
        if v <= 0:
            raise ValueError("chunk_size must be a positive integer.")
        return v

    def chunk_text(self, text: str | Any, *args, **kwargs) -> List[str]:
        """
        Splits the input text into fixed-length chunks.

        Parameters:
        - text (Union[str, Any]): The input text to be chunked.

        Returns:
        - List[str]: A list of text chunks, each of a specified fixed length.
        """
        # Check if the input is a string, if not, attempt to convert to a
        # string.
        if not isinstance(text, str):
            text = str(text)

        # Using list comprehension to split text into chunks of fixed size
        chunks = [
            text[i : i + self.chunk_size]
            for i in range(0, len(text), self.chunk_size)
        ]

        return chunks
