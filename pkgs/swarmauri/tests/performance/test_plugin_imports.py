

def test_import_multiple_first_class_plugins():
    from swarmauri.llms import OpenAIModel, GroqModel
    from swarmauri.agents import QAAgent

    assert OpenAIModel is not None
    assert GroqModel is not None
    assert QAAgent is not None
