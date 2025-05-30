class DummyLLM:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class DummyAgent:
    def __init__(self, llm=None):
        self.llm = llm
        self.conversation = type('Conv', (), {})()

    def exec(self, prompt, llm_kwargs=None):
        return f"executed:{prompt}"
