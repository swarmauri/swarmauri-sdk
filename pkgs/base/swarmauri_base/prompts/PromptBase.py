from typing import Optional, Literal
from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.prompts.IPrompt import IPrompt

class PromptBase(IPrompt, ComponentBase):
    """
    The ChatPrompt class represents a simple, chat-like prompt system where a 
    message can be set and retrieved as needed. It's particularly useful in 
    applications involving conversational agents, chatbots, or any system that 
    requires dynamic text-based interactions.
    """
    prompt: str = ""
    resource: Optional[str] =  Field(default=ResourceTypes.PROMPT.value, frozen=True)
    type: Literal['PromptBase'] = 'PromptBase'

    def __call__(self):
        """
        Enables the instance to be callable, allowing direct retrieval of the message. 
        This method facilitates intuitive access to the prompt's message, mimicking callable 
        behavior seen in functional programming paradigms.
        
        Returns:
        - str: The current message stored in the prompt.
        """
        return self.prompt

    def set_prompt(self, prompt: str):
        """
        Updates the internal message of the chat prompt. This method provides a way to change 
        the content of the prompt dynamically, reflecting changes in the conversational context 
        or user inputs.
        
        Parameters:
        - message (str): The new message to set for the prompt.
        """
        self.prompt = prompt