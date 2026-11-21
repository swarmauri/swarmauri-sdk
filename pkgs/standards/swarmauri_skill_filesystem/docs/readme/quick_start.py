from swarmauri_skill_filesystem import FileSystemSkill

skill = FileSystemSkill.from_path("./my-skill")
print(skill.instructions)
