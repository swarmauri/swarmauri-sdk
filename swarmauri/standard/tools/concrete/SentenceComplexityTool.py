# swarmauri/standard/tools/concrete/SentenceComplexity.py

from typing import List, Literal, Dict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from pydantic import Field
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter

class SentenceComplexityTool(ToolBase):
    version: str = "0.1.dev1"
    parameters: List[Parameter] = Field(default_factory=lambda: [
        Parameter(
            name="text",
            type="string",
            description="The text to analyze for sentence complexity.",
            required=True
        )
    ])

    name: str = 'SentenceComplexityTool'
    description: str = "Evaluates sentence complexity based on average sentence length and the number of clauses."
    type: Literal['SentenceComplexityTool'] = 'SentenceComplexityTool'

    def __call__(self, text: str) -> Dict[str, float]:
        """
        Evaluate sentence complexity based on average sentence length and the number of clauses.

        Parameters:
        - text (str): The text to analyze.

        Returns:
        - dict: A dictionary containing average sentence length and average number of clauses per sentence.
        """
        nltk.download('punkt')
        sentences = sent_tokenize(text)

        num_sentences = len(sentences)
        total_words = sum(len(word_tokenize(sentence)) for sentence in sentences)
        clauses = sum(sentence.count(',') + sentence.count(';') + 1 for sentence in sentences)

        avg_sentence_length = total_words / num_sentences
        avg_clauses_per_sentence = clauses / num_sentences

        return {
            "average_sentence_length": avg_sentence_length,
            "average_clauses_per_sentence": avg_clauses_per_sentence
        }