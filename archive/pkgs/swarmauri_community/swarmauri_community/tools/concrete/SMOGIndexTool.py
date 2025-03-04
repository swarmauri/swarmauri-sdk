from typing import List, Literal, Dict
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter
import re
import math
import nltk
from nltk.tokenize import sent_tokenize


# Download required NLTK data once during module load

nltk.download("punkt_tab", quiet=True)


class SMOGIndexTool(ToolBase):
    version: str = "0.1.dev2"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text to analyze for SMOG Index",
                required=True,
            )
        ]
    )
    name: str = "SMOGIndexTool"
    description: str = "Calculates the SMOG Index for the provided text."
    type: Literal["SMOGIndexTool"] = "SMOGIndexTool"

    def __call__(self, text: str) -> Dict[str, float]:
        """
        Calculates the SMOG Index for the provided text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            Dict[str, float]: The calculated SMOG Index.
        """
        return {"smog_index": self.calculate_smog_index(text)}

    def calculate_smog_index(self, text: str) -> float:
        """
        Calculate the SMOG Index for a given text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            float: The calculated SMOG Index.
        """
        sentences = self.count_sentences(text)
        polysyllables = self.count_polysyllables(text)

        if sentences == 0:
            return 0.0  # Avoid division by zero

        smog_index = 1.0430 * math.sqrt(polysyllables * (30 / sentences)) + 3.1291
        return round(smog_index, 1)

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

    def count_polysyllables(self, text: str) -> int:
        """
        Count the number of polysyllabic words (words with three or more syllables) in the text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            int: The number of polysyllabic words in the text.
        """
        words = re.findall(r"\w+", text)
        return len([word for word in words if self.count_syllables(word) >= 3])

    def count_syllables(self, word: str) -> int:
        """
        Count the number of syllables in a given word.

        Parameters:
            word (str): The word to analyze.

        Returns:
            int: The number of syllables in the word.
        """
        word = word.lower()
        vowels = "aeiouy"
        count = 0
        if word and word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith("e") and not word.endswith("le"):
            count -= 1
        if count == 0:
            count = 1
        return count
