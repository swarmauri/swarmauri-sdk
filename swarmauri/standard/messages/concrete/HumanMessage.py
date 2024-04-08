from swarmauri.standard.messages.base.MessageBase import MessageBase

class HumanMessage(MessageBase):
    """
    Represents a message created by a human user.

    Extends the `Message` class to specifically represent messages input by human users in a conversational
    interface. It contains the message content and assigns the type "HumanMessage" to distinguish it from
    other types of messages.
    """

    def __init__(self, content, name=None):
        """
        Initializes a new instance of HumanMessage with specified content.

        Args:
            content (str): The text content of the human-created message.
            name (str, optional): The name of the human sender.
        """
        super().__init__(role='user', content=content)

