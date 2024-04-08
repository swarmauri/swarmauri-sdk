from swarmauri.standard.messages.base.MessageBase import MessageBase


class FunctionMessage(MessageBase):
    """
    Represents a message created by a human user.

    This class extends the `Message` class to specifically represent messages that
    are input by human users in a conversational interface. It contains the message
    content and assigns the type "HumanMessage" to distinguish it from other types
    of messages.

    Attributes:
        content (str): The text content of the message.

    Methods:
        display: Returns a dictionary representation of the message for display,
                 tagging it with the role "user".
    """

    def __init__(self, content, name, tool_call_id):
        super().__init__(role='tool', content=content)
        self.name = name
        self.tool_call_id = tool_call_id
    