from abc import ABC, abstractmethod
from typing import Any, Union


class IPromptTemplate(ABC):
    """
    Interface for template-based prompt generation within the SwarmAURI
    framework.
    Defines standard operations and attributes for managing and utilizing
    templates.
    """

    @abstractmethod
    def __call__(self, **kwargs: dict[str, Any]) -> str:
        """
        Abstract method that subclasses must implement to define the behavior
        of the prompt template when called.

        """

    @abstractmethod
    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.

        Args:
            template (str): The new template string to be used for generating
            prompts.
        """

    @abstractmethod
    def set_variables(
        self, variables: Union[list[dict[str, Any]], dict[str, Any]] = {}
    ) -> None:
        """
        Sets or updates the variables to be substituted into the template.

        Args:
            variables (List[Dict[str, str]]): A dictionary of variables where
            each key-value
                                        pair corresponds to a placeholder name
                                        and its
                                        replacement value in the template.
        """

    @abstractmethod
    def generate_prompt(self, **kwargs: dict[str, Any]) -> str:
        """
        Generates a prompt string based on the current template and provided
        keyword arguments.

        Args:
            **kwargs Dict[str, Any]: Keyword arguments containing variables for
            template substitution.

        Returns:
            str: The generated prompt string with template variables replaced
            by their
                 corresponding values provided in `kwargs`.
        """
