import pytest
from swarmauri.standard.messages.concrete.AgentMessage import AgentMessage

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        message = AgentMessage(content='test')
        assert message.resource == 'Message'
    test()

@pytest.mark.unit
def content_test():
    def test():
        message = AgentMessage(content='test')
        assert message.content == 'test'
    test()

@pytest.mark.unit
def role_test():
    def test():
        message = AgentMessage(content='test')
        assert message.role == 'assistant'
    test()