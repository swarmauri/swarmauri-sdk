import re
import string
from typing import Dict, List, Union, Optional, Literal
from pydantic import Field

import warnings

from swarmauri_core.prompt_templates.IPromptTemplate import IPromptTemplate
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class PromptTemplateBase(IPromptTemplate, ComponentBase):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template manipulation.
    """

    template: str = ""
    variables: Union[List[Dict[str, str]], Dict[str, str]] = {}
    resource: Optional[str] = Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal["PromptTemplateBase"] = "PromptTemplateBase"

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
        warnings.warn("Deprecating 'generate_prompt()', use `fill()`.")
        return self.fill(variables)

    def fill(self, variables: Dict[str, str] = None) -> str:
        variables = variables or self.variables
        safe_vars = {}
        for key, value in variables.items():
            if not isinstance(key, str) or not key.isidentifier():
                raise ValueError(f"Invalid variable name: {key!r}")
            safe_vars[key] = value
        template = string.Template(self.template)
        try:
            return template.substitute(safe_vars)
        except KeyError as e:
            raise KeyError(f"Missing template variable: {e.args[0]}") from e

    def __call__(self, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a prompt using the current template and provided keyword arguments for substitution.
        """
        variables = variables if variables else self.variables
        return self.generate_prompt(variables)
