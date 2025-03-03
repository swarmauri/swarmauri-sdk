import nltk
import textstat
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter

# Download necessary NLTK resources
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger_eng")


class LexicalDensityTool(ToolBase):
    version: str = "0.1.dev2"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text for which to calculate the Lexical Density.",
                required=True,
            )
        ]
    )

    name: str = "LexicalDensityTool"
    description: str = "Calculates the lexical density of a text, indicating the proportion of lexical words."
    type: Literal["LexicalDensityTool"] = "LexicalDensityTool"

    def __call__(self, text: str) -> Dict[str, float]:
        """
        Calculates the Lexical Density score for the given text.

        Parameters:
        - text (str): The text to analyze.

        Returns:
        - Dict[str, float]: A dictionary containing the Lexical Density score.
        """
        return {"lexical_density": self.calculate_lexical_density(text)}

    def calculate_lexical_density(self, text: str) -> float:
        """
        Calculates the Lexical Density score for the given text.

        Args:
            text (str): The text to analyze.

        Returns:
            float: The Lexical Density score as a percentage.
        """
        # Total number of words in the text
        total_words = textstat.lexicon_count(text, removepunct=True)

        # Total number of lexical words (content words)
        lexical_words = self.count_lexical_words(text)

        # Calculate lexical density
        if total_words == 0:
            return 0.0

        lexical_density = (lexical_words / total_words) * 100
        return lexical_density

    def count_lexical_words(self, text: str) -> int:
        """
        Counts the number of lexical words (nouns, verbs, adjectives, adverbs) in the text.

        Args:
            text (str): The text to analyze.

        Returns:
            int: The number of lexical words in the text.
        """
        words = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(words)

        # POS tags for lexical words (nouns, verbs, adjectives, adverbs)
        lexical_pos_tags = {
            "NN",
            "NNS",
            "NNP",
            "NNPS",
            "VB",
            "VBD",
            "VBG",
            "VBN",
            "VBP",
            "VBZ",
            "JJ",
            "JJR",
            "JJS",
            "RB",
            "RBR",
            "RBS",
        }

        lexical_words = [word for word, pos in pos_tags if pos in lexical_pos_tags]
        return len(lexical_words)
