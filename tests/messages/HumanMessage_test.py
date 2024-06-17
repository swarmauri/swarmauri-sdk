import pytest
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage

@pytest.mark.unit
def test_ubc_resource():
    def test():
        message = HumanMessage(content='test')
        assert message.resource == 'Message'
    test()

@pytest.mark.unit
def test_content():
    def test():
        message = HumanMessage(content='test')
        assert message.content == 'test'
    test()

@pytest.mark.unit
def test_role():
    def test():
        message = HumanMessage(content='test')
        assert message.role == 'user'
    test()