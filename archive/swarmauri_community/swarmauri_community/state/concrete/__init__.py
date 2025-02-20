from swarmauri.utils._lazy_import import _lazy_import

state_files = [
    ("swarmauri_community.state.concrete.ClipboardState", "ClipboardState"),
]

for module_name, class_name in state_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in state_files]
