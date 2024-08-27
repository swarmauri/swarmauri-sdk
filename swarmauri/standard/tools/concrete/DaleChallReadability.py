from typing import List, Literal
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class DaleChallReadabilityTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text to calculate the Dale-Chall readability score for.",
                required=True,
            ),
        ]
    )
    name: str = "DaleChallReadabilityTool"
    description: str = "Calculates the Dale-Chall readability score for a given text."
    type: Literal["DaleChallReadabilityTool"] = "DaleChallReadabilityTool"

    def __call__(self, text: str) -> float:
        """
        Calculates the Dale-Chall readability score for a given text.

        Parameters:
            text (str): The text to analyze.

        Returns:
            float: The Dale-Chall readability score.
        """
        return self.calculate_dale_chall_score(text)

    def calculate_dale_chall_score(self, text: str) -> float:
        # Preliminary data: word frequency list, constants
        easy_words = self.get_easy_words()
        sentences = self.get_sentences(text)
        words = self.get_words(text)

        # Count the number of difficult words
        difficult_words = [word for word in words if word not in easy_words]
        num_difficult_words = len(difficult_words)

        # Calculate the Dale-Chall readability score
        num_words = len(words)
        num_sentences = len(sentences)

        avg_sentence_length = num_words / num_sentences if num_sentences else 0
        percent_difficult_words = (num_difficult_words / num_words) * 100 if num_words else 0

        dale_chall_score = 0.1579 * percent_difficult_words + 0.0496 * avg_sentence_length
        if percent_difficult_words > 5:
            dale_chall_score += 3.6365

        return round(dale_chall_score, 2)

    def get_easy_words(self) -> set:
        easy_word_set = set()
        # Load the list of easy words (this is a sample list)
        easy_words = """
        a,able,about,above,accept,accident
        please replace this list with the actual Dale-Chall easy word list.
        """
        for word in easy_words.split(','):
            easy_word_set.add(word.strip().lower())
        return easy_word_set

    def get_sentences(self, text: str) -> List[str]:
        import re
        return re.split(r'[.!?]', text)

    def get_words(self, text: str) -> List[str]:
        import re
        return re.findall(r'\b\w+\b', text.lower())