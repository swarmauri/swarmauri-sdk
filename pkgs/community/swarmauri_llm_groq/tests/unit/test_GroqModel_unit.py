from swarmauri_llm_groq import GroqModel


def test_groqmodel_import() -> None:
    assert GroqModel.__name__ == "GroqModel"
