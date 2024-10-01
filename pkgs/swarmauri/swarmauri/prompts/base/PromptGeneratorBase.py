from typing import Dict, List, Generator, Any, Union, Optional, Literal
from pydantic import Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.prompts.IPrompt import IPrompt
from swarmauri_core.prompts.ITemplate import ITemplate


class PromptGeneratorBase(IPrompt, ITemplate, ComponentBase):
    """
    A class that generates prompts based on a template and a list of variable sets.
    It implements the IPrompt and ITemplate interfaces.
    """

    template: str = ""
    variables: Union[List[Dict[str, Any]], Dict[str, Any]] = {}
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptGeneratorBase'] = 'PromptGeneratorBase'

    def set_template(self, template: str) -> None:
        self.template = template

    def set_variables(self, variables: List[Dict[str, Any]]) -> None:
        self.variables = variables

    def generate_prompt(self, variables: Dict[str, Any]) -> str:
        """
        Generates a prompt using the provided variables if any
        else uses the next variables set in the list.
        """
        variables = variables if variables else self.variables.pop(0) if self.variables else {}
        return self.template.format(**variables)

    def __call__(self) -> Generator[str, None, None]:
        """
        Returns a generator that yields prompts constructed from the template and 
        each set of variables in the variables list.
        """
        for variables_set in self.variables:
            yield self.generate_prompt(variables_set)
        self.variables = []