from swarmauri.core.prompts.IPrompt import IPrompt

class Prompt(IPrompt):
    """
    The ChatPrompt class represents a simple, chat-like prompt system where a 
    message can be set and retrieved as needed. It's particularly useful in 
    applications involving conversational agents, chatbots, or any system that 
    requires dynamic text-based interactions.
    """

    def __init__(self, prompt: str = ""):
        """
        Initializes an instance of ChatPrompt with an optional initial message.
        
        Parameters:
        - message (str, optional): The initial message for the prompt. Defaults to an empty string.
        """
        self.prompt = prompt

    def __call__(self, prompt):
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
