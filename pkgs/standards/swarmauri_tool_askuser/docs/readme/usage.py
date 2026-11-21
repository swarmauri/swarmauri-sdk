from swarmauri_tool_askuser import AskUserTool

ask = AskUserTool(input_handler=lambda question: input(question.content + " "))
answer = ask("Which package?", choices=["core", "base"])
print(answer.answer)
