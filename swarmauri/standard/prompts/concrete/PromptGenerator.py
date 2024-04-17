from typing import Dict, List, Generator
from swarmauri.core.prompts.IPrompt import IPrompt
from swarmauri.core.prompts.ITemplate import ITemplate


class PromptGenerator(IPrompt, ITemplate):
    """
    A class that generates prompts based on a template and a list of variable sets.
    It implements the IPrompt and ITemplate interfaces.
    """

    def __init__(self, template: str = "", variables: List[Dict[str, str]] = []):
        self._template = template
        self._variables_list = variables

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, value: str) -> None:
        self._template = value

    @property
    def variables(self) -> List[Dict[str, str]]:
        return self._variables_list

    @variables.setter
    def variables(self, value: List[Dict[str, str]]) -> None:
        if not isinstance(value, list):
            raise ValueError("Expected a list of dictionaries for variables.")
        self._variables_list = value

    def set_template(self, template: str) -> None:
        self._template = template

    def set_variables(self, variables: List[Dict[str, str]]) -> None:
        self.variables = variables

    def generate_prompt(self, **kwargs) -> str:
        """
        Generates a prompt using the provided variables if any, 
        else uses the next variables set in the list.
        """
        variables = kwargs if kwargs else self.variables.pop(0) if self.variables else {}
        return self._template.format(**variables)

    def __call__(self) -> Generator[str, None, None]:
        """
        Returns a generator that yields prompts constructed from the template and 
        each set of variables in the variables list.
        """
        for variables_set in self._variables_list:
            yield self.generate_prompt(**variables_set)
        self._variables_list = []  # Reset the list after all prompts have been generated.