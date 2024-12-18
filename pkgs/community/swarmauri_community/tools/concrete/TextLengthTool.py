from swarmauri_core.typing import SubclassUnion
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download required NLTK data once during module load
nltk.download("punkt", quiet=True)


class TextLengthTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text to analyze for length.",
                required=True,
            )
        ]
    )
    name: str = "TextLengthTool"
    description: str = "Calculates the length of the provided text in terms of characters, words, and sentences."
    type: Literal["TextLengthTool"] = "TextLengthTool"

    def __call__(self, text: str) -> Dict[str, int]:
        """
        Calculates the length of the provided text in terms of characters, words, and sentences.

        Parameters:
            text (str): The text to analyze.

        Returns:
            dict: A dictionary containing the number of characters, words, and sentences.
        """
        return self.calculate_text_length(text)

    def calculate_text_length(self, text: str) -> Dict[str, int]:
        """
        Calculate the length of the text in characters, words, and sentences.

        Parameters:
            text (str): The text to analyze.

        Returns:
            dict: A dictionary containing:
                  - 'num_characters': Number of characters in the text.
                  - 'num_words': Number of words in the text.
                  - 'num_sentences': Number of sentences in the text.
        """
        num_characters = self.count_characters(text)
        num_words = self.count_words(text)
        num_sentences = self.count_sentences(text)

        return {
            "num_characters": num_characters,
            "num_words": num_words,
            "num_sentences": num_sentences,
        }

    def count_characters(self, text: str) -> int:
        """
        Count the number of characters in the text, excluding spaces.

        Parameters:
            text (str): The text to analyze.

        Returns:
            int: The number of characters in the text.
        """
        return len(text.replace(" ", ""))

    def count_words(self, text: str) -> int:
        """
        Count the number of words in the text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            int: The number of words in the text.
        """
        words = word_tokenize(text)
        return len(words)

    def count_sentences(self, text: str) -> int:
        """
        Count the number of sentences in the text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            int: The number of sentences in the text.
        """
        sentences = sent_tokenize(text)
        return len(sentences)


SubclassUnion.update(
    baseclass=ToolBase,
    type_name="TextLengthTool",
    obj=TextLengthTool,
)
