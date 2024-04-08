from typing import Dict
from ....core.prompts.IPrompt import IPrompt

class PromptTemplate(IPrompt):
    """
    A class that represents a template for generating prompts, 
    allowing dynamic content insertion into pre-defined template slots.

    Attributes:
        template (str): A string template with placeholders for content insertion.
        variables (Dict[str, str]): A dictionary mapping placeholder names in the template to their content.
    """

    def __init__(self, template: str = "", variables: Dict[str, str] = {}):
        """
        Initializes a new instance of the PromptTemplate class.

        Args:
            template (str): The string template for the prompt.
            variables (Dict[str, str]): A dictionary mapping variables in the template to their values.
        """
        self.template = template
        self.variables = variables

    def __call__(self, variables: Dict[str, str] = {}):
        """
        Generates the prompt string by substituting variables into the template.

        Returns:
            str: The generated prompt with variables substituted.
        """
        variables = variables or self.variables
        formatted_prompt = self.template.format(**variables)
        return formatted_prompt

    def set_template(self, template: str):
        """
        Sets a new template string for the prompt.

        Args:
            template (str): The new string template to use.
        """
        self.template = template

    def set_variables(self, variables: Dict[str, str]):
        """
        Sets the variables to be substituted into the template.

        Args:
            variables (Dict[str, str]): A dictionary of variables to be substituted into the template.
        
        Raises:
            TypeError: If the provided variables argument is not a dictionary.
        """
        if isinstance(variables, dict):
            self.variables = variables
        else:
            raise TypeError("Invalid type. Expected dict for variables.")