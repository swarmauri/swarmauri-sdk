from typing import Dict, List, Union, Optional, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.prompts.IPrompt import IPrompt
from swarmauri_core.prompts.ITemplate import ITemplate

class PromptTemplateBase(IPrompt, ITemplate, ComponentBase):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template manipulation.
    """

    template: str = ""
    variables: Union[List[Dict[str, str]], Dict[str,str]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptTemplateBase'] = 'PromptTemplateBase'

    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.
        """
        self.template = template

    def set_variables(self, variables: Dict[str, str]) -> None:
        """
        Sets or updates the variables to be substituted into the template.
        """
        self.variables = variables

    def generate_prompt(self, variables: Dict[str, str] = None) -> str:
        variables = variables or self.variables
        return self.template.format(**variables)

    def __call__(self, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a prompt using the current template and provided keyword arguments for substitution.
        """
        variables = variables if variables else self.variables
        return self.generate_prompt(variables)