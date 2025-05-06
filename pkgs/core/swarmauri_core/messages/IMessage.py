from abc import ABC


class IMessage(ABC):
    """
    An abstract interface representing a general message structure.

    This interface defines the basic attributes that all
    messages should have, including type, name, and content,
    and requires subclasses to implement representation and formatting methods.
    """
