import warnings
from typing import Literal, Union

from pydantic import Field
from swarmauri_core.prompt_templates.IPromptTemplate import IPromptTemplate

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class PromptTemplateBase(IPromptTemplate, ComponentBase):
    """
    A class for generating prompts based on a template and variables.
    Implements the IPrompt for generating prompts and ITemplate for template
    manipulation.
    """

    template: str = ""
    variables: Union[list[dict[str, str]], dict[str, str]] = {}
    resource: str | None = Field(
        default=ResourceTypes.PROMPT.value, frozen=True
    )
    type: Literal["PromptTemplateBase"] = "PromptTemplateBase"

    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string.
        """
        self.template = template

    def set_variables(self, variables: dict[str, str]) -> None:
        """
        Sets or updates the variables to be substituted into the template.
        """
        self.variables = variables

    def generate_prompt(self, variables: dict[str, str] = None) -> str:
        warnings.warn("Deprecating 'generate_prompt()', use `fill()`.")
        return self.fill(variables)

    def fill(self, variables: dict[str, str] = None) -> str:
        variables = variables or self.variables
        return self.template.format(**variables)

    def __call__(self, variables: dict[str, str] | None = None) -> str:
        """
        Generates a prompt using the current template and provided keyword
        arguments for substitution.
        """
        variables = variables if variables else self.variables
        return self.generate_prompt(variables)
