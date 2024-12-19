from swarmauri.utils.LazyLoader import LazyLoader

toolkits_files = [
    ("swarmauri_community.toolkits.concrete.GithubToolkit", "GithubToolkit"),
]

for module_name, class_name in toolkits_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

__all__ = [class_name for _, class_name in toolkits_files]
