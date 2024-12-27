from swarmauri_core.typing import SubclassUnion
import re
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class FleschReadingEaseTool(ToolBase):
    version: str = "0.1.0.dev11"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text for which to calculate the Flesch Reading Ease score.",
                required=True,
            )
        ]
    )

    name: str = "FleschReadingEaseTool"
    description: str = (
        "Calculates the readability of text using the Flesch Reading Ease formula."
    )
    type: Literal["FleschReadingEaseTool"] = "FleschReadingEaseTool"

    def __call__(self, text: str) -> Dict[str, float]:
        """
        Calculates the Flesch Reading Ease score for the given text.

        Parameters:
        - text (str): The text to analyze.

        Returns:
        - float: The Flesch Reading Ease score.
        """
        return {"flesch_reading_ease": self.calculate_flesch_reading_ease(text)}

    def calculate_flesch_reading_ease(self, text: str) -> float:
        """
        Calculates the Flesch Reading Ease score for the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            float: The Flesch Reading Ease score.
        """
        # Count the number of sentences in the text
        sentences = text.count(".") + text.count("!") + text.count("?")
        sentences = max(sentences, 1)  # Avoid division by zero

        # Split the text into words
        words = re.findall(r"\b\w+\b", text)
        num_words = len(words)
        num_words = max(num_words, 1)  # Avoid division by zero

        # Count the number of syllables in the text
        syllables = sum(self.count_syllables(word) for word in words)

        # Calculate the Flesch Reading Ease score
        score = (
            206.835 - 1.015 * (num_words / sentences) - 84.6 * (syllables / num_words)
        )
        return score

    def count_syllables(self, word: str) -> int:
        """
        Counts the number of syllables in a given word.

        Args:
            word (str): The word to analyze.

        Returns:
            int: The number of syllables in the word.
        """
        word = word.lower()
        vowels = "aeiouy"
        num_syllables = 0
        prev_char = None

        for i, char in enumerate(word):
            if char in vowels:
                if prev_char is None or prev_char not in vowels:
                    num_syllables += 1
            prev_char = char

        # Adjust for silent 'e' at the end
        if word.endswith("e"):
            num_syllables -= 1

        # Adjust for "le" at the end of the word when preceded by a consonant
        if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
            num_syllables += 1

        # Ensure at least one syllable per word
        return max(num_syllables, 1)


SubclassUnion.update(
    baseclass=ToolBase, type_name="FleschReadingEaseTool", obj=FleschReadingEaseTool
)
