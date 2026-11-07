from enum import Enum


class BidirectionalStreamState(str, Enum):
    NEW = "new"
    OPEN = "open"
    CLOSING = "closing"
    CLOSED = "closed"
    FAILED = "failed"
