from typing import List, Literal, Dict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from pydantic import Field
from swarmauri.tools.base.ToolBase import ToolBase
from swarmauri.tools.concrete.Parameter import Parameter

# Download required NLTK data once during module load

nltk.download("punkt_tab", quiet=True)


class SentenceComplexityTool(ToolBase):
    version: str = "0.1.dev2"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="text",
                type="string",
                description="The text to analyze for sentence complexity.",
                required=True,
            )
        ]
    )

    name: str = "SentenceComplexityTool"
    description: str = "Evaluates sentence complexity based on average sentence length and the number of clauses."
    type: Literal["SentenceComplexityTool"] = "SentenceComplexityTool"

    def __call__(self, text: str) -> Dict[str, float]:
        """
        Evaluate sentence complexity based on average sentence length and the number of clauses.

        Parameters:
        - text (str): The text to analyze.

        Returns:
        - dict: A dictionary containing average sentence length and average number of clauses per sentence.
        """
        if not text.strip():
            raise ValueError("Input text cannot be empty.")

        sentences = sent_tokenize(text)
        num_sentences = len(sentences)

        if num_sentences == 0:
            return {"average_sentence_length": 0.0, "average_clauses_per_sentence": 0.0}

        total_words = 0
        total_clauses = 0

        for sentence in sentences:
            words = word_tokenize(sentence)
            total_words += len(words)

            # Improved clause counting method

            clauses = sentence.count(",") + sentence.count(";")
            clauses += sum(
                sentence.lower().count(conj)
                for conj in [
                    "and",
                    "but",
                    "or",
                    "because",
                    "although",
                    "though",
                    "while",
                    "if",
                ]
            )
            total_clauses += clauses + 1

        avg_sentence_length = total_words / num_sentences
        avg_clauses_per_sentence = total_clauses / num_sentences

        return {
            "average_sentence_length": avg_sentence_length,
            "average_clauses_per_sentence": avg_clauses_per_sentence,
        }
