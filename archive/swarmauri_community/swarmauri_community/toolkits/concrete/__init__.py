from swarmauri.utils._lazy_import import _lazy_import

toolkits_files = [
    ("swarmauri_community.toolkits.concrete.GithubToolkit", "GithubToolkit"),
]

for module_name, class_name in toolkits_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

__all__ = [class_name for _, class_name in toolkits_files]
