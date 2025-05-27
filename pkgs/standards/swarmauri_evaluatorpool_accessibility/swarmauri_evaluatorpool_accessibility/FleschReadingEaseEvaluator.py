import os
import re
from typing import Any, Dict, Literal, Tuple

from pydantic import PrivateAttr

import nltk
from nltk.corpus import cmudict
from nltk.tokenize import sent_tokenize, word_tokenize
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.programs.Program import Program


# Custom download dir for environments like CI
NLTK_DATA_DIR = os.getenv("NLTK_DATA_DIR", "/tmp/nltk_data")
nltk.data.path.append(NLTK_DATA_DIR)


@ComponentBase.register_type(EvaluatorBase, "FleschReadingEaseEvaluator")
class FleschReadingEaseEvaluator(EvaluatorBase, ComponentBase):
    """
    Evaluator that computes the Flesch Reading Ease score for text content.

    The Flesch Reading Ease score is a readability metric that uses sentence length
    and syllable count to determine how easy a text is to read. The formula is:
    FRE = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)

    Higher scores (closer to 100) indicate text that is easier to read, while lower
    scores indicate more complex text.

    Attributes:
        type: The type identifier for this evaluator
    """

    type: Literal["FleschReadingEaseEvaluator"] = "FleschReadingEaseEvaluator"
    _cmu_dict = PrivateAttr(default=None)

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def evaluate(self, program: Program, **kwargs) -> Dict[str, Any]:
        """Return ``{"score": float, "metadata": dict}`` for the given program."""
        score, meta = self._compute_score(program, **kwargs)
        return {"score": score, "metadata": meta}

    def __init__(self, **kwargs):
        """Initialize the Flesch Reading Ease evaluator."""
        super().__init__(**kwargs)
        # Download necessary NLTK resources if not already present
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            if self.logger:
                self.logger.info("Downloading NLTK punkt tokenizer")
            nltk.download("punkt", quiet=True, download_dir=NLTK_DATA_DIR)

        try:
            nltk.data.find("corpora/cmudict")
        except LookupError:
            if self.logger:
                self.logger.info("Downloading CMU Pronouncing Dictionary")
            nltk.download("cmudict", quiet=True, download_dir=NLTK_DATA_DIR)

        # Load the CMU dictionary for syllable counting
        self._cmu_dict = cmudict.dict() if cmudict else None

    @property
    def cmu_dict(self):
        """Access the CMU Pronouncing Dictionary used for syllable counts."""
        return self._cmu_dict

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute the Flesch Reading Ease score for the given program.

        Args:
            program: The program containing text to evaluate
            **kwargs: Additional parameters for the evaluation process

        Returns:
            A tuple containing:
                - float: The Flesch Reading Ease score (0-100, higher is easier to read)
                - Dict[str, Any]: Metadata including sentence and syllable statistics

        Raises:
            ValueError: If the text cannot be processed
        """
        # Extract text from the program
        text = self._get_program_text(program)
        if not text or not isinstance(text, str):
            if self.logger:
                self.logger.warning("Program content is empty or not a string")
            return 0.0, {"error": "No valid text content found"}

        # Clean the text (remove extra whitespace, etc.)
        text = self._clean_text(text)

        # Tokenize the text into sentences and words
        sentences = sent_tokenize(text)
        words = word_tokenize(text)

        # Filter out punctuation from words
        words = [word for word in words if re.match(r"\w+", word)]

        # Count sentences, words, and syllables
        sentence_count = len(sentences)
        word_count = len(words)

        if sentence_count == 0 or word_count == 0:
            if self.logger:
                self.logger.warning("Text contains no sentences or words")
            return 0.0, {"error": "Text contains no sentences or words"}

        # Count syllables in each word
        total_syllables = sum(self._count_syllables(word) for word in words)

        # Calculate average sentence length and syllables per word
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = total_syllables / word_count

        # Calculate Flesch Reading Ease score
        # FRE = 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)
        fre_score = (
            206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        )

        # Ensure score is within 0-100 range
        fre_score = max(0, min(100, fre_score))

        # Prepare metadata
        metadata = {
            "sentence_count": sentence_count,
            "word_count": word_count,
            "syllable_count": total_syllables,
            "avg_sentence_length": avg_sentence_length,
            "avg_syllables_per_word": avg_syllables_per_word,
            "readability_interpretation": self._interpret_score(fre_score),
        }

        if self.logger:
            self.logger.info(
                f"Flesch Reading Ease score: {fre_score:.2f} ({metadata['readability_interpretation']})"
            )
        return fre_score, metadata

    def _get_program_text(self, program: Program) -> str:
        """Return program text by joining its source files."""
        try:
            source_files = program.get_source_files()
            if isinstance(source_files, dict):
                return " \n".join(str(v) for v in source_files.values())
        except Exception as exc:
            if self.logger:
                self.logger.debug(f"Failed to obtain program text: {exc}")
        return ""

    def _clean_text(self, text: str) -> str:
        """
        Clean text by removing extra whitespace and normalizing.

        Args:
            text: The input text to clean

        Returns:
            Cleaned text
        """
        # Replace multiple whitespace with a single space
        text = re.sub(r"\s+", " ", text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

    def _count_syllables(self, word: str) -> int:
        """
        Count the number of syllables in a word.

        Uses the CMU Pronouncing Dictionary if available, otherwise falls back
        to a heuristic method.

        Args:
            word: The word to count syllables for

        Returns:
            The number of syllables in the word
        """
        word = word.lower()

        # Try using CMU dictionary first
        if self._cmu_dict and word in self._cmu_dict:
            # Count vowel phonemes (indicated by digits in the CMU dict)
            return max(
                1,
                sum(
                    1
                    for phoneme in self._cmu_dict[word][0]
                    if any(c.isdigit() for c in phoneme)
                ),
            )

        # Fallback to heuristic method
        # Count vowel groups
        vowels = "aeiouy"
        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char.lower() in vowels
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        # Handle special cases
        if word.endswith("e") and not word.endswith("le"):
            count -= 1
        if word.endswith("es") or word.endswith("ed") and len(word) > 2:
            if word[-3] not in vowels:
                count -= 1
        if count == 0:  # Every word has at least one syllable
            count = 1

        return count

    def _interpret_score(self, score: float) -> str:
        """
        Provide a human-readable interpretation of the Flesch Reading Ease score.

        Args:
            score: The Flesch Reading Ease score (0-100)

        Returns:
            A string describing the readability level
        """
        if score >= 90:
            return "Very Easy (5th grade)"
        elif score >= 80:
            return "Easy (6th grade)"
        elif score >= 70:
            return "Fairly Easy (7th grade)"
        elif score >= 60:
            return "Standard (8th-9th grade)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (College graduate level)"
