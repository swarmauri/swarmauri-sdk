from swarmauri.utils._lazy_import import _lazy_import

# List of task_mgt_strategies names (file names without the ".py" extension) and corresponding class names
task_mgt_strategies_files = [
    ("swarmauri_standard.task_mgt_strategies.RoundRobinStrategy", "RoundRobinStrategy"),
]

# Lazy loading of task_mgt_strategies classes, storing them in variables
for module_name, class_name in task_mgt_strategies_files:
    globals()[class_name] = _lazy_import(module_name, class_name)

# Adding the lazy-loaded state classes to __all__
__all__ = [class_name for _, class_name in task_mgt_strategies_files]
