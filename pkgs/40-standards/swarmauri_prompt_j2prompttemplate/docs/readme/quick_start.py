from swarmauri_prompt_j2prompttemplate import J2PromptTemplate

template = J2PromptTemplate(template="Hello, {{ name }}!")
result = template({"name": "World"})
print(result)  # Hello, World!
