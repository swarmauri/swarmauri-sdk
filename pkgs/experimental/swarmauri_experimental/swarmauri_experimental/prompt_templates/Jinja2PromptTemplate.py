# pip install Jinja2

from typing import Dict, Optional, Literal
from pydantic import ConfigDict
from jinja2 import Template

from swarmauri_core.ComponentBase import ComponentBase
from swarmauri_base.prompts.PromptTemplateBase import PromptTemplateBase  # Assuming PromptTemplateBase is accessible

@ComponentBase.register_type(PromptTemplateBase, 'Jinja2PromptTemplate')
class Jinja2PromptTemplate(PromptTemplateBase):
    """
    A subclass of PromptTemplateBase that uses Jinja2 for template rendering.
    """

    # Holds the compiled Jinja2 template
    compiled_template: Optional[Template] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: Literal['Jinja2PromptTemplate'] =  'Jinja2PromptTemplate'
    
    def set_template(self, template: str) -> None:
        """
        Sets or updates the current template string and compiles it using Jinja2.
        """
        self.template = template
        self.compiled_template = Template(template)

    def generate_prompt(self, variables: Dict[str, str] = None) -> str:
        """
        Generates a prompt using Jinja2 rendering with the current template and provided variables.
        """
        variables = variables or self.variables
        # Ensure the template has been compiled; compile if not present.
        if not self.compiled_template:
            self.compiled_template = Template(self.template)
        return self.compiled_template.render(**variables)

    def fill(self, variables: Dict[str, str] = None) -> str:
        variables = variables or self.variables
        return self.template.format(**variables)

    def __call__(self, variables: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a prompt using Jinja2 templating when the instance is called.
        """
        variables = variables if variables else self.variables
        return self.generate_prompt(variables)
