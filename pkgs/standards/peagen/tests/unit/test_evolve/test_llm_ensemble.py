from peagen.llm.ensemble import LLMEnsemble

class FakeBackend:
    def generate(self, prompt, temperature=0.7, max_tokens=4096):
        return "ok"


def test_generate_auto(monkeypatch):
    LLMEnsemble._backends = {"fake": FakeBackend}
    monkeypatch.setattr(LLMEnsemble, "_discover", lambda: None)
    monkeypatch.setattr(LLMEnsemble, "_choose_backend", lambda name: "fake")
    res = LLMEnsemble.generate("p")
    assert res == "ok"
    assert LLMEnsemble._metrics_tokens["fake"] > 0
