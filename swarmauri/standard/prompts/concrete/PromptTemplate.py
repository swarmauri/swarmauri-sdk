from typing import Dict, List
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate

class PromptTemplate(IPrompt, ITemplate):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template manipulation.
    """

    def __init__(self, template: str = "", variables: List[Dict[str, str]] = []):
        self._template = template
        self._variables_list = variables

    @property
    def template(self) -> str:
        """
        Get the current prompt template.
        """
        return self._template

    @template.setter
    def template(self, value: str) -> None:
        """
        Set a new template string for the prompt.
        """
        self._template = value

    @property
    def variables(self) -> List[Dict[str, str]]:
        """
        Get the current set of variables for the template.
        """
        return self._variables_list 

    @variables.setter
    def variables(self, value: List[Dict[str, str]]) -> None:
        if not isinstance(value, list):
            raise ValueError("Variables must be a list of dictionaries.")
        self._variables_list = value

    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.
        """
        self._template = template

    def set_variables(self, variables: Dict[str, str]) -> None:
        """
        Sets or updates the variables to be substituted into the template.
        """
        self._variables_list = variables

    def generate_prompt(self, variables: List[Dict[str, str]] = None) -> str:
        variables = variables.pop(0) or (self._variables_list.pop(0) if self._variables_list else {})
        return self._template.format(**variables)

    def __call__(self, variables: List[Dict[str, str]]) -> str:
        """
        Generates a prompt using the current template and provided keyword arguments for substitution.
        """
        return self.generate_prompt(variables)