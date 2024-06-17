import pytest
from swarmauri.standard.messages.concrete.SystemMessage import SystemMessage

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        message = SystemMessage(content='test')
        assert message.resource == 'Message'
    test()

@pytest.mark.unit
def content_test():
    def test():
        message = SystemMessage(content='test')
        assert message.content == 'test'
    test()

@pytest.mark.unit
def role_test():
    def test():
        message = SystemMessage(content='test')
        assert message.role == 'system'
    test()