from swarmauri.utils.LazyLoader import LazyLoader

# List of control_panels names (file names without the ".py" extension) and corresponding class names
control_panels_files = [
    ("swarmauri.control_panels.concrete.ControlPanel", "ControlPanel"),
]

# Lazy loading of task_mgt_strategies classes, storing them in variables
for module_name, class_name in control_panels_files:
    globals()[class_name] = LazyLoader(module_name, class_name)

# Adding the lazy-loaded state classes to __all__
__all__ = [class_name for _, class_name in control_panels_files]
