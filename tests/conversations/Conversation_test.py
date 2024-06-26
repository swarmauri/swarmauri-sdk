import pytest
import os
from swarmauri.standard.conversations.concrete.Conversation import Conversation

@pytest.mark.unit
def test_ubc_resource():
    def test():
        conversation = Conversation()
        assert conversation.resource == 'Conversation'
    test()
