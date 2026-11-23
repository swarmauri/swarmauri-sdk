from swarmauri_skill_local import LocalSkill

skill = LocalSkill.from_name("my-skill", roots=["./skills"])
print(skill.name)
