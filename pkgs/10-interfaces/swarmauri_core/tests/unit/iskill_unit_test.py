from swarmauri_core.skills import ISkill


def test_iskill_importable():
    assert ISkill.__name__ == "ISkill"
