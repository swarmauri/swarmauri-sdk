import pytest
import os
from swarmauri.standard.conversations.concrete.Conversation import Conversation

@pytest.mark.unit
def test_ubc_resource():
    conversation = Conversation()
    assert conversation.resource == 'Conversation'

@pytest.mark.unit
def test_ubc_type():
    conversation = Conversation()
    assert conversation.type == 'Conversation'

@pytest.mark.unit
def test_serialization():
    conversation = Conversation()
    assert conversation.id == Conversation.model_validate_json(conversation.model_dump_json()).id