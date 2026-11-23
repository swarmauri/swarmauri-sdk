from swarmauri_state_clipboard import ClipboardState

state = ClipboardState()
state.write({"session": "abc123", "step": 1})

print(state.read())

state.update({"step": 2})
print(state.read())
