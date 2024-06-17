import pytest
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        message = HumanMessage(content='test')
        assert message.resource == 'Message'
    test()

@pytest.mark.unit
def content_test():
    def test():
        message = HumanMessage(content='test')
        assert message.content == 'test'
    test()

@pytest.mark.unit
def role_test():
    def test():
        message = HumanMessage(content='test')
        assert message.role == 'user'
    test()