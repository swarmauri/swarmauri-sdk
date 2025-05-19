import logging
import os
import re
from typing import Any, Dict, List, Literal, Tuple

import markdown
from bs4 import BeautifulSoup
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_standard.programs.Program import Program

logger = logging.getLogger(__name__)


@ComponentBase.register_type(EvaluatorBase, "AutomatedReadabilityIndexEvaluator")
class AutomatedReadabilityIndexEvaluator(EvaluatorBase, ComponentBase):
    """
    Evaluator that computes the Automated Readability Index (ARI) score for text content.

    This evaluator parses text from various file formats (.txt, .md, .html),
    counts characters, words, and sentences, and applies the ARI formula to estimate
    the U.S. grade level readability of the content.

    The ARI formula is: 4.71*(characters/words) + 0.5*(words/sentences) - 21.43

    Attributes:
        type: The type identifier for this evaluator
    """

    type: Literal["AutomatedReadabilityIndexEvaluator"] = (
        "AutomatedReadabilityIndexEvaluator"
    )
    model_config = {"arbitrary_types_allowed": True, "exclude": {"logger"}}

    def _compute_score(
        self, program: Program, **kwargs
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Compute the Automated Readability Index (ARI) score for a program's text content.

        Args:
            program: The program to evaluate
            **kwargs: Additional parameters for the evaluation process

        Returns:
            A tuple containing:
                - float: The ARI score (higher means more complex text)
                - Dict[str, Any]: Metadata including character, word, and sentence counts

        Raises:
            ValueError: If no text content could be extracted from the program
        """
        logger.info(f"Computing ARI score for program: {program.name}")

        # Extract text content from program artifacts
        text_content = self._extract_text_from_program(program)

        if not text_content:
            logger.warning("No text content found in program artifacts")
            return 0.0, {
                "error": "No text content found",
                "chars": 0,
                "words": 0,
                "sentences": 0,
            }

        # Count characters, words, and sentences
        char_count = len(text_content)
        word_count = len(self._count_words(text_content))
        sentence_count = len(self._count_sentences(text_content))

        logger.debug(
            f"Text statistics: {char_count} chars, {word_count} words, {sentence_count} sentences"
        )

        # Handle edge cases to avoid division by zero
        if word_count == 0 or sentence_count == 0:
            logger.warning(
                "Cannot compute ARI: division by zero (no words or sentences)"
            )
            return 0.0, {
                "error": "Cannot compute ARI: no words or sentences",
                "chars": char_count,
                "words": word_count,
                "sentences": sentence_count,
            }

        # Calculate ARI score
        # ARI = 4.71*(characters/words) + 0.5*(words/sentences) - 21.43
        ari_score = (
            4.71 * (char_count / word_count)
            + 0.5 * (word_count / sentence_count)
            - 21.43
        )

        # Ensure score is non-negative (ARI can theoretically go below 0 for very simple text)
        ari_score = max(0.0, ari_score)

        logger.info(f"Computed ARI score: {ari_score:.2f}")

        return ari_score, {
            "chars": char_count,
            "words": word_count,
            "sentences": sentence_count,
        }

    def _extract_text_from_program(self, program: Program) -> str:
        """
        Extract text content from program artifacts.

        Handles different file types (.txt, .md, .html) and extracts plain text.

        Args:
            program: The program containing artifacts to extract text from

        Returns:
            A string containing all the extracted text content
        """
        text_content = []

        # Get all artifacts from the program
        artifacts = program.get_artifacts()

        for artifact in artifacts:
            file_path = artifact.get_path()
            if not file_path or not os.path.exists(file_path):
                logger.debug(f"Skipping non-existent artifact: {file_path}")
                continue

            # Process based on file extension
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            try:
                if ext in [".txt"]:
                    # Plain text files
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        text_content.append(f.read())

                elif ext in [".md", ".markdown"]:
                    # Markdown files - convert to HTML then extract text
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        md_content = f.read()
                        html_content = markdown.markdown(md_content)
                        soup = BeautifulSoup(html_content, "html.parser")
                        text_content.append(soup.get_text())

                elif ext in [".html", ".htm"]:
                    # HTML files
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        html_content = f.read()
                        soup = BeautifulSoup(html_content, "html.parser")
                        text_content.append(soup.get_text())

            except Exception as e:
                logger.error(f"Error extracting text from {file_path}: {str(e)}")

        return " ".join(text_content)

    def _count_words(self, text: str) -> List[str]:
        """
        Count words in the given text.

        Args:
            text: The text to analyze

        Returns:
            A list of words found in the text
        """
        # Split by whitespace and filter out empty strings
        words = [word for word in re.findall(r"\b\w+\b", text.lower()) if word]
        return words

    def _count_sentences(self, text: str) -> List[str]:
        """
        Count sentences in the given text.

        Uses regular expressions to identify sentence boundaries based on
        common punctuation patterns.

        Args:
            text: The text to analyze

        Returns:
            A list of sentences found in the text
        """
        # Handle common sentence terminators and edge cases
        # This regex looks for sentence-ending punctuation followed by space or end of string
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Filter out empty sentences
        sentences = [s for s in sentences if s.strip()]

        # If no sentences were found but there is text, count it as one sentence
        if not sentences and text.strip():
            return [text]

        return sentences
