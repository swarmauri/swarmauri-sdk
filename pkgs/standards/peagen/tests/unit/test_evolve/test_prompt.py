from peagen.prompt_sampler import PromptSampler


def test_build_mutate_prompt(tmp_path):
    parent = "def f(x):\n    return x"
    insp = ["print(1)"]
    prompt = PromptSampler.build_mutate_prompt(parent, insp, "f(x)")
    assert "inspiration 1" in prompt
    assert "def f(x):" in prompt
