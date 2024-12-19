from swarmauri.utils.LazyLoader import LazyLoader

state_files = [
    ("swarmauri_community.state.concrete.ClipboardState", "ClipboardState"),
]

for module_name, class_name in state_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in state_files]
