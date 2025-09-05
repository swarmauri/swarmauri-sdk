from typing import Dict, List, Literal

from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "SearchWordTool")
class SearchWordTool(ToolBase):
    """
    A tool for searching for a specific word or phrase in a file and highlighting occurrences.

    Attributes:
        version (str): The version of the tool.
        name (str): The name of the tool.
        type (Literal["SearchWordTool"]): The type of the tool.
        description (str): A brief description of what the tool does.
        parameters (List[Parameter]): The parameters for configuring the tool.
    """

    version: str = "0.1.dev1"
    name: str = "SearchWordTool"
    type: Literal["SearchWordTool"] = "SearchWordTool"
    description: str = (
        "Searches for a specific word or phrase in a file and highlights occurrences."
    )
    parameters: List[str] = ["file_path", "search_word"]

    def __call__(self, file_path: str, search_word: str) -> Dict[str, List[str]]:
        """
        Executes the search tool and returns the occurrences of the search word.

        Parameters:
            file_path (str): The path to the file to search in.
            search_word (str): The word or phrase to search for.

        Returns:
            Dict[str, List[str]]: A dictionary containing the highlighted lines and the count of occurrences.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the input data is invalid.
        """
        if self.validate_input(file_path, search_word):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    text = file.readlines()

                occurrences, count_occurances = self.search_in_file(text, search_word)
                logger.info(
                    f"Found {count_occurances} occurrences of '{search_word}' in {file_path}."
                )
                return {"lines": occurrences, "count": count_occurances}
            except FileNotFoundError as e:
                logger.error(f"File not found: {file_path}")
                raise e
        else:
            raise ValueError("Invalid input for SearchWordTool.")

    def search_in_file(self, lines: List[str], search_word: str) -> List[str]:
        """
        Searches for the specified word in the provided lines and highlights it.

        Parameters:
            lines (List[str]): The lines of the file to search through.
            search_word (str): The word or phrase to search for.

        Returns:
            List[str]: A list of lines with the search word highlighted.
        """
        occurrence_count = 0
        highlighted_lines = []
        search_word_lower = search_word.lower()

        for line in lines:
            line_stripped = line.rstrip("\n")
            # Count occurrences in the current line (case-insensitive)
            occurrence_count += line.lower().count(search_word_lower)
            if search_word_lower in line.lower():
                # Highlight the entire line in red
                highlighted_line = f"\033[1;31m{line_stripped}\033[0m"
                highlighted_lines.append(highlighted_line)
            else:
                highlighted_lines.append(line_stripped)

        return highlighted_lines, occurrence_count

    def validate_input(self, file_path: str, search_word: str) -> bool:
        """
        Validates the input parameters for the search tool.

        Parameters:
            file_path (str): The path of the file to search in.
            search_word (str): The word or phrase to search for.

        Returns:
            bool: True if the inputs are valid, False otherwise.
        """
        if isinstance(file_path, str) and isinstance(search_word, str):
            return True
        return False
